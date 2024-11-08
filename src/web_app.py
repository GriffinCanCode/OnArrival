from flask import Flask, request, jsonify, render_template, send_from_directory
from src.services.location_alert_system import LocationAlertSystem
import os

# Get directory paths
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Initialize Flask app with explicit template and static folders
app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# Initialize the location alert system
alert_system = LocationAlertSystem()

# Get the Flask app from the notification service
app = alert_system.notification_service.app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/send_leisure', methods=['POST'])
def send_leisure_alert():
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            })

        group = data.get('group')
        message = data.get('message')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            })

        success = True
        error_message = None
        
        for contact in alert_system.contacts:
            result = alert_system.notification_service.make_call(
                contact.phone,
                message,
                include_follow_up=True
            )
            if not result:
                success = False
                error_message = f"Failed to send alert to {contact.name}"
                break
        
        return jsonify({
            'success': success,
            'error': error_message
        })
    except Exception as e:
        print(f"Error in send_leisure_alert: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/send_business', methods=['POST'])
def send_business_alert():
    try:
        data = request.json
        business_name = data.get('business_name')
        phone = data.get('phone')
        message = data.get('message')
        
        result = alert_system.notification_service.make_call(
            phone,
            message,
            business_name=business_name,
            include_follow_up=True
        )
        
        return jsonify({
            'success': result,
            'error': None if result else "Failed to send alert"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/groups', methods=['GET', 'POST'])
def handle_groups():
    if request.method == 'GET':
        return jsonify(alert_system.contact_storage.load_groups())
    elif request.method == 'POST':
        try:
            data = request.json
            group_name = data.get('name')
            alert_system.contact_storage.add_group(group_name)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })