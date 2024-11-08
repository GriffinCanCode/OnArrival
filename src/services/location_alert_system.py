from models.location import Location
from models.contact import Contact
from services.contact_storage import ContactStorage
from services.notification_service import NotificationService
from services.location_service import LocationService

class LocationAlertSystem:
    def __init__(self):
        self.contact_storage = ContactStorage()
        self.notification_service = NotificationService()
        self.location_service = LocationService()
        
        self.locations = Location.create_default_locations()
        self.contacts = self.contact_storage.load_contacts()

    def add_contact(self, name: str, phone_number: str) -> None:
        contact = Contact(name, phone_number)
        self.contacts.append(contact)
        self.contact_storage.save_contacts(self.contacts)

    def delete_contact(self, contact: Contact) -> None:
        self.contacts = [c for c in self.contacts if c.phone != contact.phone]
        self.contact_storage.delete_contact(contact)