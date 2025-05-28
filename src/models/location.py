import os
import json

class Location:
    def __init__(self, name: str, coords: tuple, radius: float, message: str):
        self.name = name
        self.coords = coords
        self.radius = radius
        self.message = message
        self.status = False  # Track if we're currently in this location

    @classmethod
    def _load_location_templates(cls):
        """Load location templates from JSON configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'message_templates.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config['location_templates']
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load location templates from config file: {e}")
            # Fallback to basic templates
            return {
                "general": {
                    "name": "General Location",
                    "message": "This is an automated service message. The traveler has arrived at their destination and will be available shortly."
                }
            }

    @classmethod
    def create_default_locations(cls) -> dict:
        templates = cls._load_location_templates()
        
        return {
            "California": cls(
                "California",
                (36.7783, -119.4179),
                50,
                templates.get("california", templates["general"])["message"]
            ),
            "DC": cls(
                "DC",
                (38.9072, -77.0369),
                20,
                templates.get("dc", templates["general"])["message"]
            )
        } 