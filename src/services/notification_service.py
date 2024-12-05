from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from flask import Flask
import os
from dotenv import load_dotenv

class NotificationService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        
        # Get Twilio credentials from environment variables
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Script templates
        self.script_templates = {
            "Landing": {
                "main": "Hello (), Griffin the Goat has arrived at his destination safely.",
                "follow_up": "Thank you for listening, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
            },
            "Eagle": {
                "main": "Hello (), The eagle has inevitably landed and will be back shortly. Prepare appropiately. Eagle noises, et cetera.",
                "follow_up": "If you did not receieve the phone call, this was a scheduled public security announcement of Good Man Griffin's arrival. Thank you for listening, if you did, the G.O.A.T. approaches and is thankful for your time. He will see you shortly and expects your highest energy level."
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
        
        # Validate credentials exist
        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            raise ValueError("Missing required Twilio credentials in environment variables")
            
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            print(f"Failed to initialize Twilio client: {str(e)}")
            raise

    def run(self):
        """Run the Flask server"""
        self.app.run(port=5001)

    def send_message(self, to_number, message):
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_number
            )
            return True, message.sid
        except Exception as e:
            print(f"Failed to send message: {str(e)}")
            return False, str(e)

    def make_call(self, to_number: str, message: str, business_name: str = None, include_follow_up: bool = True) -> bool:
        try:
            # Create TwiML for direct message delivery
            response = VoiceResponse()
            response.pause(length=1)
            if business_name:
                response.say(f"Message from {business_name}.", voice='alice', rate=0.8)
                response.pause(length=1)
            response.say(message, voice='alice', rate=0.8)
            
            # Make the call
            call = self.client.calls.create(
                twiml=str(response),
                to=to_number,
                from_=self.twilio_number
            )
            
            print(f"Call initiated to {to_number}: {call.sid}")
            
            if include_follow_up:
                # Find the matching template by comparing the main message
                template_name = None
                for name, template in self.script_templates.items():
                    # Strip whitespace and compare normalized strings
                    template_msg = template["main"].strip().lower()
                    input_msg = message.strip().lower()
                    if template_msg in input_msg or input_msg in template_msg:
                        template_name = name
                        break
                
                # If no matching template found, use Custom Message
                if template_name is None:
                    template_name = "Custom Message"
                    print(f"No matching template found for message, using {template_name}")
                
                # Send follow-up text message
                success, msg_sid = self.send_message(
                    to_number,
                    self.script_templates[template_name]["follow_up"]
                )
                
                if success:
                    print(f"Follow-up text sent to {to_number} using {template_name} template: {msg_sid}")
                else:
                    print(f"Failed to send follow-up text to {to_number}")
            
            return True
            
        except Exception as e:
            print(f"Error making call: {str(e)}")
            return False

    def get_script_templates(self):
        """Returns the dictionary of available script templates"""
        return {name: template["main"] for name, template in self.script_templates.items()}

    def get_full_script_templates(self):
        """Returns the complete dictionary of available script templates including follow-up messages"""
        return self.script_templates

    def add_script_template(self, name: str, template: str):
        """Adds a new script template"""
        self.script_templates[name] = template