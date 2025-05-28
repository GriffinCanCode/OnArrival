import os
import secrets
from typing import Dict, List, Optional

class SecurityConfig:
    """Centralized security configuration"""
    
    def __init__(self):
        # Load from environment or use secure defaults
        self.secret_key = os.getenv('SECRET_KEY') or self._generate_secret_key()
        self.session_timeout_minutes = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # API Keys configuration
        self.api_keys = self._load_api_keys()
        
        # CORS configuration
        self.allowed_origins = self._get_allowed_origins()
        
        # Rate limiting configuration
        self.default_rate_limits = {
            'auth': {'max_requests': 20, 'window_seconds': 3600},  # 20 per hour
            'api': {'max_requests': 100, 'window_seconds': 3600},   # 100 per hour  
            'send_alerts': {'max_requests': 50, 'window_seconds': 3600}  # 50 per hour
        }
        
        # Content validation limits
        self.validation_limits = {
            'max_request_size': 50 * 1024,  # 50KB
            'max_message_length': 1600,
            'max_name_length': 100,
            'max_business_name_length': 100,
            'min_timer_minutes': 1,
            'max_timer_minutes': 120,
            'max_groups_per_user': 50,
            'max_contacts_per_group': 100
        }
        
        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key if none is provided"""
        key = secrets.token_hex(32)
        print(f"⚠️  Generated temporary secret key. Set SECRET_KEY environment variable for production!")
        return key
    
    def _load_api_keys(self) -> Dict[str, Dict]:
        """Load API keys from environment or generate defaults"""
        api_keys = {}
        
        # Development key
        dev_key = os.getenv('API_KEY_DEVELOPMENT')
        if not dev_key:
            dev_key = secrets.token_hex(32)
            if self.environment == 'development':
                print(f"🔑 Generated development API key: {dev_key}")
        
        api_keys[dev_key] = {
            'name': 'development',
            'permissions': ['send_alerts', 'manage_contacts', 'view_groups'],
            'rate_limit': 100,  # requests per hour
            'environment': 'development'
        }
        
        # Production key (only load if in production)
        if self.environment == 'production':
            prod_key = os.getenv('API_KEY_PRODUCTION')
            if prod_key:
                api_keys[prod_key] = {
                    'name': 'production',
                    'permissions': ['send_alerts', 'manage_contacts', 'view_groups'],
                    'rate_limit': 200,
                    'environment': 'production'
                }
            else:
                print("⚠️  No production API key configured!")
        
        return api_keys
    
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed CORS origins"""
        origins_str = os.getenv('ALLOWED_ORIGINS', 'http://localhost:*,http://127.0.0.1:*')
        return [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    
    def get_rate_limit(self, endpoint_type: str) -> Dict[str, int]:
        """Get rate limit configuration for an endpoint type"""
        return self.default_rate_limits.get(endpoint_type, {'max_requests': 100, 'window_seconds': 3600})
    
    def get_validation_limit(self, limit_type: str) -> int:
        """Get validation limit for a specific type"""
        return self.validation_limits.get(limit_type, 0)
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == 'production'
    
    def validate_api_key(self, api_key: str) -> Optional[Dict]:
        """Validate an API key and return its information"""
        return self.api_keys.get(api_key)
    
    def get_api_key_permissions(self, api_key: str) -> List[str]:
        """Get permissions for an API key"""
        key_info = self.validate_api_key(api_key)
        return key_info.get('permissions', []) if key_info else []
    
    def print_security_summary(self):
        """Print a summary of security configuration"""
        print("\n🔒 Security Configuration Summary:")
        print(f"   Environment: {self.environment}")
        print(f"   Session Timeout: {self.session_timeout_minutes} minutes")
        print(f"   API Keys Configured: {len(self.api_keys)}")
        print(f"   CORS Origins: {len(self.allowed_origins)}")
        print(f"   Max Request Size: {self.validation_limits['max_request_size']} bytes")
        print(f"   Security Headers: {len(self.security_headers)} configured")
        
        if self.is_development():
            print("\n⚠️  Development Mode Warnings:")
            print("   - Detailed error messages enabled")
            print("   - CORS configured for localhost")
            print("   - Debug mode may be enabled")
        
# Global security configuration instance
security_config = SecurityConfig() 