import os
import secrets
import hashlib
import time
import jwt
from functools import wraps
from flask import request, jsonify, session
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AuthenticationManager:
    """Handles API authentication and session management"""
    
    def __init__(self):
        # Load API keys from environment or generate defaults
        self.api_keys = self._load_api_keys()
        self.secret_key = os.getenv('SECRET_KEY') or secrets.token_hex(32)
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30')) * 60  # Convert to seconds
        
        # Track failed authentication attempts
        self.failed_attempts = {}
        self.lockout_duration = 300  # 5 minutes lockout
        self.max_failed_attempts = 5
    
    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from environment variables"""
        api_keys = {}
        
        # Load from environment variables
        main_api_key = os.getenv('ONARRIVAL_API_KEY')
        if main_api_key:
            api_keys[main_api_key] = {
                'name': 'main',
                'permissions': ['send_alerts', 'manage_contacts', 'manage_groups'],
                'rate_limit': 100  # requests per hour
            }
        
        # Load additional API keys (format: ONARRIVAL_API_KEY_NAME=key)
        for key, value in os.environ.items():
            if key.startswith('ONARRIVAL_API_KEY_') and key != 'ONARRIVAL_API_KEY':
                key_name = key.replace('ONARRIVAL_API_KEY_', '').lower()
                api_keys[value] = {
                    'name': key_name,
                    'permissions': ['send_alerts'],  # Limited permissions by default
                    'rate_limit': 50
                }
        
        # If no API keys are configured, create a default one (for development only)
        if not api_keys:
            default_key = os.getenv('DEFAULT_API_KEY', 'dev-key-' + secrets.token_hex(16))
            print(f"⚠️  WARNING: Using default API key for development: {default_key}")
            print("⚠️  Please set ONARRIVAL_API_KEY in production!")
            
            api_keys[default_key] = {
                'name': 'development',
                'permissions': ['send_alerts', 'manage_contacts', 'manage_groups'],
                'rate_limit': 1000
            }
        
        return api_keys
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return key info if valid"""
        if not api_key:
            return None
        
        # Check if IP is locked out
        client_ip = self._get_client_ip()
        if self._is_ip_locked_out(client_ip):
            return None
        
        if api_key in self.api_keys:
            # Reset failed attempts on successful auth
            if client_ip in self.failed_attempts:
                del self.failed_attempts[client_ip]
            
            return self.api_keys[api_key]
        else:
            # Track failed attempt
            self._record_failed_attempt(client_ip)
            return None
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        else:
            return request.environ.get('REMOTE_ADDR', 'unknown')
    
    def _record_failed_attempt(self, ip: str):
        """Record a failed authentication attempt"""
        current_time = time.time()
        
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        # Clean old attempts
        self.failed_attempts[ip] = [
            timestamp for timestamp in self.failed_attempts[ip]
            if current_time - timestamp < self.lockout_duration
        ]
        
        # Add current attempt
        self.failed_attempts[ip].append(current_time)
    
    def _is_ip_locked_out(self, ip: str) -> bool:
        """Check if IP is locked out due to too many failed attempts"""
        if ip not in self.failed_attempts:
            return False
        
        current_time = time.time()
        
        # Clean old attempts
        self.failed_attempts[ip] = [
            timestamp for timestamp in self.failed_attempts[ip]
            if current_time - timestamp < self.lockout_duration
        ]
        
        return len(self.failed_attempts[ip]) >= self.max_failed_attempts
    
    def has_permission(self, key_info: Dict[str, Any], permission: str) -> bool:
        """Check if API key has specific permission"""
        return permission in key_info.get('permissions', [])
    
    def create_session_token(self, api_key_info: Dict[str, Any]) -> str:
        """Create a JWT session token"""
        payload = {
            'key_name': api_key_info['name'],
            'permissions': api_key_info['permissions'],
            'iat': time.time(),
            'exp': time.time() + self.session_timeout
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

# Global authentication manager instance
auth_manager = AuthenticationManager()

def require_api_key(permission: str = None):
    """
    Decorator to require valid API key authentication
    
    Args:
        permission: Specific permission required (optional)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header or query parameter
            api_key = (
                request.headers.get('X-API-Key') or 
                request.headers.get('Authorization', '').replace('Bearer ', '') or
                request.args.get('api_key')
            )
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': 'API key required. Include X-API-Key header or api_key parameter.'
                }), 401
            
            # Validate API key
            key_info = auth_manager.validate_api_key(api_key)
            if not key_info:
                return jsonify({
                    'success': False,
                    'error': 'Invalid API key or too many failed attempts. Please try again later.'
                }), 401
            
            # Check specific permission if required
            if permission and not auth_manager.has_permission(key_info, permission):
                return jsonify({
                    'success': False,
                    'error': f'API key does not have required permission: {permission}'
                }), 403
            
            # Store key info in request context for use in the route
            request.api_key_info = key_info
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_session_token(permission: str = None):
    """
    Decorator to require valid session token
    
    Args:
        permission: Specific permission required (optional)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get session token from header
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({
                    'success': False,
                    'error': 'Session token required. Include Authorization header with Bearer token.'
                }), 401
            
            # Validate session token
            session_data = auth_manager.validate_session_token(token)
            if not session_data:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired session token'
                }), 401
            
            # Check specific permission if required
            if permission and permission not in session_data.get('permissions', []):
                return jsonify({
                    'success': False,
                    'error': f'Session does not have required permission: {permission}'
                }), 403
            
            # Store session data in request context
            request.session_data = session_data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_csrf_token() -> str:
    """Generate CSRF token for web forms"""
    return secrets.token_hex(32)

def validate_csrf_token(token: str, session_token: str) -> bool:
    """Validate CSRF token"""
    expected_token = session.get('csrf_token')
    return token and expected_token and secrets.compare_digest(token, expected_token)

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}
    
    def is_allowed(self, key: str, limit: int, window_seconds: int = 3600) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests outside the window
        self.requests[key] = [
            (timestamp, count) for timestamp, count in self.requests[key]
            if current_time - timestamp < window_seconds
        ]
        
        # Count total requests in current window
        total_requests = sum(count for _, count in self.requests[key])
        
        if total_requests >= limit:
            return False
        
        # Add current request
        # Try to group with recent requests to save memory
        if self.requests[key] and current_time - self.requests[key][-1][0] < 60:
            # Group requests within 1 minute
            last_timestamp, last_count = self.requests[key][-1]
            self.requests[key][-1] = (last_timestamp, last_count + 1)
        else:
            self.requests[key].append((current_time, 1))
        
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """
    Decorator to apply rate limiting to endpoints
    
    Args:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds (default: 1 hour)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use API key name if available, otherwise use IP address
            if hasattr(request, 'api_key_info'):
                rate_key = f"api_key:{request.api_key_info['name']}"
                key_limit = request.api_key_info.get('rate_limit', max_requests)
            else:
                rate_key = f"ip:{auth_manager._get_client_ip()}"
                key_limit = max_requests
            
            if not rate_limiter.is_allowed(rate_key, key_limit, window_seconds):
                return jsonify({
                    'success': False,
                    'error': f'Rate limit exceeded. Maximum {key_limit} requests per hour.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 