import os
import json

DEFAULT_LANDING_MESSAGE = (
    "Don't hang up, this is an automated service message. "
    "Would you mind getting everything ready? We'll be there soon. "
    "And uh... make sure to dispose of this phone right after - it's gonna self-destruct."
)


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
            return {"general": {"name": "General Location", "message": DEFAULT_LANDING_MESSAGE}}

    @classmethod
    def create_default_locations(cls) -> dict:
        templates = cls._load_location_templates()
        general = templates.get("general", {"message": DEFAULT_LANDING_MESSAGE})

        def landing(key):
            return templates.get(key, general).get("message") or DEFAULT_LANDING_MESSAGE

        return {
            "California": cls("California", (36.7783, -119.4179), 50, landing("california")),
            "DC": cls("DC", (38.9072, -77.0369), 20, landing("dc")),
        }
