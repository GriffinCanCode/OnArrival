from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

class LocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="location_alert_app")

    def get_current_location(self) -> tuple:
        """Get current location using IP-based geolocation"""
        try:
            response = requests.get('https://ipapi.co/json/')
            data = response.json()
            return (data['latitude'], data['longitude'])
        except:
            return (0, 0)  # Default coordinates if location fetch fails

    def calculate_distance(self, point1: tuple, point2: tuple) -> float:
        return geodesic(point1, point2).km

    def is_within_radius(self, current_location: tuple, target_location: tuple, radius: float) -> bool:
        return self.calculate_distance(current_location, target_location) <= radius