from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_cors import CORS
import os
import secrets
import argparse
from src.services.location_alert_system import LocationAlertSystem
from utils.validation import InputValidator, SecurityValidator, ValidationResult
from utils.auth import require_api_key, rate_limit, auth_manager, generate_csrf_token

# Get directory paths
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Initialize the location alert system
alert_system = LocationAlertSystem()

# Get the Flask app from the notification service and configure it properly
app = alert_system.notification_service.app
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Configure template and static directories
app.template_folder = template_dir
app.static_folder = static_dir

# Enable CORS for development (configure appropriately for production)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:*').split(','))

@app.before_request
def before_request():
    """Security checks before processing requests"""
    # Generate CSRF token for web forms
    if 'csrf_token' not in session:
        session['csrf_token'] = generate_csrf_token()
    
    # Validate request size for API endpoints
    if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'PATCH']:
        if request.content_length and request.content_length > 50 * 1024:  # 50KB limit
            return jsonify({
                'success': False,
                'error': 'Request payload too large. Maximum size: 50KB'
            }), 413

@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        if not alert_system:
            return render_template('error.html', error="Alert system not available"), 500
        
        return render_template('index.html', csrf_token=session['csrf_token'])
    except Exception as e:
        print(f"Error serving index: {e}")
        return render_template('error.html', error="Application error"), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/auth', methods=['POST'])
@rate_limit(max_requests=20, window_seconds=3600)  # 20 auth attempts per hour
def authenticate():
    """Authenticate and get session token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON data required'
            }), 400
        
        # Validate request size
        size_result = SecurityValidator.validate_request_size(data)
        if not size_result.is_valid:
            return jsonify({
                'success': False,
                'error': size_result.error_message
            }), 400
        
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key required'
            }), 400
        
        # Validate API key
        key_info = auth_manager.validate_api_key(api_key)
        if not key_info:
            return jsonify({
                'success': False,
                'error': 'Invalid API key'
            }), 401
        
        # Create session token
        session_token = auth_manager.create_session_token(key_info)
        
        return jsonify({
            'success': True,
            'session_token': session_token,
            'permissions': key_info['permissions'],
            'expires_in': auth_manager.session_timeout
        })
    
    except Exception as e:
        print(f"Error in authenticate: {e}")
        return jsonify({
            'success': False,
            'error': 'Authentication failed'
        }), 500

@app.route('/api/send_leisure', methods=['POST'])
@require_api_key(permission='send_alerts')
@rate_limit(max_requests=50, window_seconds=3600)
def send_leisure_alert():
    """Send leisure alert with validation"""
    try:
        if not alert_system:
            return jsonify({
                'success': False,
                'error': 'Alert system not available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON data required'
            }), 400
        
        # Validate request size
        size_result = SecurityValidator.validate_request_size(data)
        if not size_result.is_valid:
            return jsonify({
                'success': False,
                'error': size_result.error_message
            }), 400
        
        # Validate inputs
        group_name = data.get('group', '').strip()
        message = data.get('message', '').strip()
        
        if not group_name:
            return jsonify({
                'success': False,
                'error': 'Group name is required'
            }), 400
        
        # Validate group name
        group_validation = InputValidator.validate_group_name(group_name)
        if not group_validation.is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid group name: {group_validation.error_message}'
            }), 400
        
        # Validate message
        message_validation = InputValidator.validate_message(message)
        if not message_validation.is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid message: {message_validation.error_message}'
            }), 400
        
        # Use sanitized values
        sanitized_group = group_validation.sanitized_value
        sanitized_message = message_validation.sanitized_value
        
        # Load and validate group exists
        groups = alert_system.contact_storage.load_groups()
        group = next((g for g in groups if g.name == sanitized_group), None)
        
        if not group:
            return jsonify({
                'success': False,
                'error': f'Group "{sanitized_group}" not found'
            }), 404
        
        if not group.contacts:
            return jsonify({
                'success': False,
                'error': f'Group "{sanitized_group}" has no contacts'
            }), 400
        
        # Send alerts to all contacts in group
        success_count = 0
        error_messages = []
        
        for contact in group.contacts:
            try:
                # Replace placeholder with contact name in message
                personalized_message = sanitized_message.replace('()', contact.name)
                result = alert_system.notification_service.make_call(
                    contact.phone,
                    personalized_message,
                    include_follow_up=True
                )
                if result:
                    success_count += 1
                else:
                    error_messages.append(f"Failed to send alert to {contact.name}")
            except Exception as e:
                error_messages.append(f"Error sending to {contact.name}: {str(e)}")
        
        if success_count == 0:
            return jsonify({
                'success': False,
                'error': 'Failed to send any alerts',
                'details': error_messages
            }), 500
        
        response_data = {
            'success': True,
            'message': f'Alerts sent to {success_count} of {len(group.contacts)} contacts'
        }
        
        if error_messages:
            response_data['warnings'] = error_messages
            
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error in send_leisure_alert: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/send_business', methods=['POST'])
@require_api_key(permission='send_alerts')
@rate_limit(max_requests=50, window_seconds=3600)
def send_business_alert():
    """Send business alert with validation"""
    try:
        if not alert_system:
            return jsonify({
                'success': False,
                'error': 'Alert system not available'
            }), 503
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'JSON data required'
            }), 400
        
        # Validate request size
        size_result = SecurityValidator.validate_request_size(data)
        if not size_result.is_valid:
            return jsonify({
                'success': False,
                'error': size_result.error_message
            }), 400
        
        # Extract and validate inputs
        business_name = data.get('business_name', '').strip()
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        use_timer = data.get('use_timer', False)
        timer_minutes = data.get('timer_minutes')
        
        # Validate business name
        business_validation = InputValidator.validate_business_name(business_name)
        if not business_validation.is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid business name: {business_validation.error_message}'
            }), 400
        
        # Validate phone number
        phone_validation = InputValidator.validate_phone_number(phone)
        if not phone_validation.is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid phone number: {phone_validation.error_message}'
            }), 400
        
        # Validate message
        message_validation = InputValidator.validate_message(message)
        if not message_validation.is_valid:
            return jsonify({
                'success': False,
                'error': f'Invalid message: {message_validation.error_message}'
            }), 400
        
        # Validate timer if used
        if use_timer:
            if timer_minutes is None:
                return jsonify({
                    'success': False,
                    'error': 'Timer minutes required when using timer'
                }), 400
            
            try:
                timer_minutes = int(timer_minutes)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Timer minutes must be a number'
                }), 400
            
            timer_validation = InputValidator.validate_timer_minutes(timer_minutes)
            if not timer_validation.is_valid:
                return jsonify({
                    'success': False,
                    'error': f'Invalid timer: {timer_validation.error_message}'
                }), 400
        
        # Use sanitized values
        sanitized_business = business_validation.sanitized_value
        sanitized_phone = phone_validation.sanitized_value
        sanitized_message = message_validation.sanitized_value
        
        # TODO: Implement timer functionality for web app if needed
        # For now, send alert immediately
        try:
            result = alert_system.notification_service.make_call(
                sanitized_phone,
                sanitized_message,
                business_name=sanitized_business,
                include_follow_up=True
            )
            
            if result:
                return jsonify({
                    'success': True,
                    'message': f'Alert sent successfully to {sanitized_business}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send alert'
                }), 500
                
        except Exception as e:
            print(f"Error sending business alert: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to send alert'
            }), 500
    
    except Exception as e:
        print(f"Error in send_business_alert: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/groups', methods=['GET'])
@require_api_key(permission='manage_contacts')
@rate_limit(max_requests=100, window_seconds=3600)
def get_groups():
    """Get all groups with validation"""
    try:
        if not alert_system:
            return jsonify({
                'success': False,
                'error': 'Alert system not available'
            }), 503
        
        groups = alert_system.contact_storage.load_groups()
        groups_data = []
        
        for group in groups:
            groups_data.append({
                'name': group.name,
                'contacts': [
                    {
                        'name': contact.name,
                        'phone': contact.phone
                    }
                    for contact in group.contacts
                ]
            })
        
        return jsonify({
            'success': True,
            'groups': groups_data
        })
    
    except Exception as e:
        print(f"Error in get_groups: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/scripts', methods=['GET'])
@require_api_key()
@rate_limit(max_requests=100, window_seconds=3600)
def get_scripts():
    """Get available message scripts"""
    try:
        if not alert_system:
            return jsonify({
                'success': False,
                'error': 'Alert system not available'
            }), 503
        
        scripts = alert_system.notification_service.get_full_script_templates()
        
        return jsonify({
            'success': True,
            'scripts': scripts
        })
    
    except Exception as e:
        print(f"Error in get_scripts: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found'
        }), 404
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    return render_template('error.html', error="Internal server error"), 500

@app.errorhandler(413)
def request_too_large(error):
    """Handle request too large errors"""
    return jsonify({
        'success': False,
        'error': 'Request payload too large'
    }), 413

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='OnArrival Web Application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    args = parser.parse_args()
    
    # Print API key information for development
    if auth_manager.api_keys:
        print("\n🔐 API Authentication Information:")
        for key, info in auth_manager.api_keys.items():
            if info['name'] == 'development':
                print(f"   Development API Key: {key}")
                print(f"   Permissions: {', '.join(info['permissions'])}")
                print(f"   Rate Limit: {info['rate_limit']} requests/hour")
    
    print("\n📚 API Documentation:")
    print("   Authentication: Include X-API-Key header or api_key parameter")
    print("   Endpoints:")
    print("   - POST /api/auth - Get session token")
    print("   - POST /api/send_business - Send business alert")
    print("   - POST /api/send_leisure - Send leisure alert")
    print("   - GET /api/groups - Get contact groups")
    print("   - GET /api/scripts - Get message templates")
    print("\n🔒 Security Features Enabled:")
    print("   - Input validation and sanitization")
    print("   - API key authentication")
    print("   - Rate limiting")
    print("   - Request size limits")
    print("   - IP-based lockout protection")
    
    app.run(debug=True, host=args.host, port=args.port)