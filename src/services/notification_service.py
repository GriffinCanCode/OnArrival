from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from flask import Flask, request
import os
import json
from dotenv import load_dotenv
from utils.validation import InputValidator, SecurityValidator, ValidationResult
import html
import logging

# Load environment variables
load_dotenv()

class NotificationService:
    def __init__(self):
        # Initialize Twilio client with validation
        try:
            self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if not all([self.account_sid, self.auth_token, self.twilio_phone]):
                raise ValueError("Missing required Twilio configuration. Please check your environment variables.")
            
            # Validate phone number format
            phone_validation = InputValidator.validate_phone_number(self.twilio_phone)
            if not phone_validation.is_valid:
                raise ValueError(f"Invalid Twilio phone number format: {phone_validation.error_message}")
            
            self.twilio_phone = phone_validation.sanitized_value
            self.client = Client(self.account_sid, self.auth_token)
            
            # Set up logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twilio client: {e}")
            raise
        
        # Initialize Flask app for webhooks
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Message templates with validation
        self.script_templates = {
            "Basic Arrival": "Hello, this is an automated notification that () has arrived safely at their destination.",
            "Custom Business": "Hello, this is an automated notification from {}. {}",
            "Detailed Arrival": "Hello, this is an automated arrival notification. () has safely reached their destination and wanted to let you know they are okay.",
            "Emergency Contact": "This is an urgent automated notification. () has indicated they need assistance. Please contact them immediately.",
            "Travel Update": "Travel update: () has arrived at their planned destination and is safe."
        }
        
        # Follow-up message
        self.follow_up_message = "Thank you for listening. This was an automated notification service. If you need to reach the traveler, please call them directly."

    def validate_call_parameters(self, to_phone: str, message: str, business_name: str = None) -> ValidationResult:
        """Validate parameters for making a call"""
        # Validate phone number
        phone_validation = InputValidator.validate_phone_number(to_phone)
        if not phone_validation.is_valid:
            return ValidationResult(False, f"Invalid phone number: {phone_validation.error_message}")
        
        # Validate message
        message_validation = InputValidator.validate_message(message)
        if not message_validation.is_valid:
            return ValidationResult(False, f"Invalid message: {message_validation.error_message}")
        
        # Validate business name if provided
        if business_name:
            business_validation = InputValidator.validate_business_name(business_name)
            if not business_validation.is_valid:
                return ValidationResult(False, f"Invalid business name: {business_validation.error_message}")
        
        return ValidationResult(True, sanitized_value="All parameters valid")

    def sanitize_call_parameters(self, to_phone: str, message: str, business_name: str = None) -> tuple:
        """Sanitize call parameters and return cleaned values"""
        phone_validation = InputValidator.validate_phone_number(to_phone)
        message_validation = InputValidator.validate_message(message)
        
        sanitized_phone = phone_validation.sanitized_value
        sanitized_message = message_validation.sanitized_value
        sanitized_business = None
        
        if business_name:
            business_validation = InputValidator.validate_business_name(business_name)
            sanitized_business = business_validation.sanitized_value
        
        return sanitized_phone, sanitized_message, sanitized_business

    def make_call(self, to_phone: str, message: str, business_name: str = None, include_follow_up: bool = False) -> bool:
        """Make a call with input validation and security checks"""
        try:
            # Validate parameters
            validation_result = self.validate_call_parameters(to_phone, message, business_name)
            if not validation_result.is_valid:
                self.logger.warning(f"Call validation failed: {validation_result.error_message}")
                return False
            
            # Sanitize parameters
            sanitized_phone, sanitized_message, sanitized_business = self.sanitize_call_parameters(
                to_phone, message, business_name
            )
            
            # Create webhook URL with validation
            base_url = os.getenv('NGROK_URL', 'http://localhost:5000')
            
            # URL encode parameters safely
            import urllib.parse
            encoded_message = urllib.parse.quote(sanitized_message)
            encoded_business = urllib.parse.quote(sanitized_business) if sanitized_business else ""
            encoded_follow_up = "true" if include_follow_up else "false"
            
            webhook_url = f"{base_url}/voice"
            webhook_url += f"?message={encoded_message}"
            if encoded_business:
                webhook_url += f"&business_name={encoded_business}"
            webhook_url += f"&include_follow_up={encoded_follow_up}"
            
            # Validate webhook URL
            url_validation = SecurityValidator.validate_url(webhook_url)
            if not url_validation.is_valid:
                self.logger.error(f"Invalid webhook URL: {url_validation.error_message}")
                return False
            
            # Make the call
            call = self.client.calls.create(
                to=sanitized_phone,
                from_=self.twilio_phone,
                url=webhook_url,
                timeout=30,
                record=False  # Don't record calls for privacy
            )
            
            self.logger.info(f"Call initiated: {call.sid} to {sanitized_phone}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error making call to {to_phone}: {str(e)}")
            return False

    def setup_routes(self):
        """Setup Flask routes with security validation"""
        
        @self.app.route('/voice', methods=['GET', 'POST'])
        def voice():
            """Handle voice webhook with input validation"""
            try:
                # Validate request method
                if request.method not in ['GET', 'POST']:
                    return "Method not allowed", 405
                
                # Get parameters with validation
                message = request.args.get('message', '').strip()
                business_name = request.args.get('business_name', '').strip()
                include_follow_up = request.args.get('include_follow_up', 'false').lower() == 'true'
                
                # Validate message parameter
                if not message:
                    return "Missing message parameter", 400
                
                # Decode URL parameters safely
                import urllib.parse
                try:
                    decoded_message = urllib.parse.unquote(message)
                    decoded_business = urllib.parse.unquote(business_name) if business_name else None
                except Exception as e:
                    self.logger.warning(f"Failed to decode URL parameters: {e}")
                    return "Invalid parameters", 400
                
                # Validate decoded parameters
                message_validation = InputValidator.validate_message(decoded_message)
                if not message_validation.is_valid:
                    self.logger.warning(f"Invalid message in webhook: {message_validation.error_message}")
                    return "Invalid message content", 400
                
                sanitized_message = message_validation.sanitized_value
                sanitized_business = None
                
                if decoded_business:
                    business_validation = InputValidator.validate_business_name(decoded_business)
                    if not business_validation.is_valid:
                        self.logger.warning(f"Invalid business name in webhook: {business_validation.error_message}")
                        # Continue without business name rather than failing
                        sanitized_business = None
                    else:
                        sanitized_business = business_validation.sanitized_value
                
                # Generate TwiML response
                return self.generate_twiml_response(sanitized_message, sanitized_business, include_follow_up)
                
            except Exception as e:
                self.logger.error(f"Error in voice webhook: {str(e)}")
                # Return a safe error response
                response = VoiceResponse()
                response.say("We're sorry, there was an error processing your call. Please try again later.")
                return str(response), 500

    def generate_twiml_response(self, message: str, business_name: str = None, include_follow_up: bool = False) -> str:
        """Generate secure TwiML response with sanitized content"""
        try:
            response = VoiceResponse()
            
            # Sanitize message content for TTS
            safe_message = self.sanitize_for_tts(message)
            
            if business_name:
                safe_business = self.sanitize_for_tts(business_name)
                # Format message with business name
                full_message = f"Hello, this is an automated notification from {safe_business}. {safe_message}"
            else:
                full_message = safe_message
            
            # Add main message
            response.say(full_message, voice='alice', language='en-US')
            
            # Add follow-up message if requested
            if include_follow_up:
                response.pause(length=1)
                safe_follow_up = self.sanitize_for_tts(self.follow_up_message)
                response.say(safe_follow_up, voice='alice', language='en-US')
            
            return str(response)
            
        except Exception as e:
            self.logger.error(f"Error generating TwiML: {str(e)}")
            # Return safe fallback response
            response = VoiceResponse()
            response.say("This is an automated notification service.")
            return str(response)

    def sanitize_for_tts(self, text: str) -> str:
        """Sanitize text for Text-to-Speech to prevent injection"""
        if not text:
            return ""
        
        # HTML escape to prevent any markup injection
        safe_text = html.escape(text, quote=False)
        
        # Remove or replace potentially problematic characters for TTS
        # Remove SSML-like tags to prevent speech synthesis injection
        import re
        safe_text = re.sub(r'<[^>]*>', '', safe_text)
        
        # Remove control characters that might affect TTS
        safe_text = ''.join(char for char in safe_text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length to prevent extremely long speeches
        max_length = 1600  # Reasonable limit for phone calls
        if len(safe_text) > max_length:
            safe_text = safe_text[:max_length] + "..."
        
        return safe_text.strip()

    def get_script_templates(self) -> dict:
        """Get available script templates"""
        return self.script_templates.copy()
    
    def get_full_script_templates(self) -> dict:
        """Get full script templates with follow-up messages"""
        templates = {}
        for name, main_script in self.script_templates.items():
            templates[name] = {
                "main": main_script,
                "follow_up": self.follow_up_message
            }
        return templates
    
    def validate_script_template(self, template: str) -> ValidationResult:
        """Validate a custom script template"""
        if not template or not isinstance(template, str):
            return ValidationResult(False, "Template must be a non-empty string")
        
        # Check for placeholder
        if '()' not in template:
            return ValidationResult(False, "Template must contain () placeholder for name insertion")
        
        # Validate message content
        message_validation = InputValidator.validate_message(template)
        if not message_validation.is_valid:
            return ValidationResult(False, f"Invalid template content: {message_validation.error_message}")
        
        return ValidationResult(True, sanitized_value=message_validation.sanitized_value)
    
    def add_custom_template(self, name: str, template: str) -> ValidationResult:
        """Add a custom script template with validation"""
        # Validate template name
        if not name or len(name.strip()) == 0:
            return ValidationResult(False, "Template name cannot be empty")
        
        name = name.strip()
        if len(name) > 50:
            return ValidationResult(False, "Template name too long (max 50 characters)")
        
        # Validate template content
        validation_result = self.validate_script_template(template)
        if not validation_result.is_valid:
            return validation_result
        
        # Add template
        self.script_templates[name] = validation_result.sanitized_value
        return ValidationResult(True, sanitized_value=f"Template '{name}' added successfully")
    
    def test_connection(self) -> ValidationResult:
        """Test Twilio connection and configuration"""
        try:
            # Validate account
            account = self.client.api.accounts(self.account_sid).fetch()
            
            # Validate phone number
            phone_numbers = self.client.incoming_phone_numbers.list(phone_number=self.twilio_phone)
            
            if not phone_numbers:
                return ValidationResult(False, f"Phone number {self.twilio_phone} not found in account")
            
            return ValidationResult(True, sanitized_value=f"Twilio connection verified for {account.friendly_name}")
            
        except Exception as e:
            return ValidationResult(False, f"Twilio connection failed: {str(e)}")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask app with security considerations"""
        if debug:
            self.logger.warning("⚠️  Running in debug mode - not suitable for production!")
        
        # In production, this should be run with a proper WSGI server like Gunicorn
        self.app.run(host=host, port=port, debug=debug)