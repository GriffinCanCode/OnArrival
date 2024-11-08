from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from pathlib import Path

class NotificationService:
    def __init__(self):
        # Load environment variables
        self._load_environment()
        
        # Get credentials from environment variables
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            print("Warning: Twilio credentials not found in environment variables")
        
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            print(f"Failed to initialize Twilio client: {str(e)}")
            self.client = None
        
        # Update the script templates to include follow-up messages
        self.script_templates = {
            "Landing": {
                "main": "Hello (), Griffin the Goat has arrived at his destination safely.",
                "follow_up": "Thank you for listening, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
            },
            "Eagle": {
                "main": "Hello (), The eagle has inevitably landed and will be back shortly. Prepare appropiately. Eagle noises, et cetera.",
                "follow_up": "Thank you for listening, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
            },
            "Familiar Soil": {
                "main": "Hello (), if you are hearing this, Griffin is back on familiar soil. Prepare for the worst but expect the best. Dreams are only what you make them. Alcohol or EMS may be required. Throw this phone after the conclusion of this message or expect second degree burns.",
                "follow_up": "Thank you for listening, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
            },
            "Custom Message": {
                "main": "",
                "follow_up": "Thank you for listening, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
            }
        }

    def _load_environment(self):
        """Load environment variables from appropriate location"""
        if 'PYTHONANYWHERE_DOMAIN' in os.environ:
            # PythonAnywhere environment - load from .env in user's home
            env_path = os.path.join('/home', os.getenv('USERNAME', ''), 'onarrival', '.env')
        else:
            # Local environment
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        load_dotenv(env_path)

    def _configure_flask(self):
        """Configure Flask based on environment"""
        if 'PYTHONANYWHERE_DOMAIN' in os.environ:
            self.app.config.update(
                SERVER_NAME=os.getenv('PYTHONANYWHERE_DOMAIN'),
                PREFERRED_URL_SCHEME='https'
            )

    def make_call(self, to_number: str, message: str, business_name: str = None, include_follow_up: bool = False) -> bool:
        try:
            # Create TwiML for direct message delivery
            response = VoiceResponse()
            response.pause(length=1)
            if business_name:
                response.say(f"Message from {business_name}.", voice='alice', rate=0.8)
                response.pause(length=1)
            response.say(message, voice='alice', rate=0.8)
            
            # Add follow-up message if requested
            if include_follow_up:
                response.pause(length=1)
                response.say(self.script_templates["Landing"]["follow_up"], voice='alice', rate=0.8)
            
            # Make the call
            call = self.client.calls.create(
                twiml=str(response),
                to=to_number,
                from_=self.from_number
            )
            
            print(f"Call initiated to {to_number}: {call.sid}")
            return True
            
        except Exception as e:
            print(f"Error making call: {str(e)}")
            return False

    def get_script_templates(self):
        """Returns the dictionary of available script templates"""
        # Return just the main messages for backwards compatibility
        return {name: template["main"] for name, template in self.script_templates.items()}

    def get_full_script_templates(self):
        """Returns the complete dictionary of available script templates including follow-up messages"""
        return self.script_templates

    def add_script_template(self, name: str, template: str):
        """Adds a new script template"""
        self.script_templates[name] = template

    def run(self):
        self.app.run(port=5001)