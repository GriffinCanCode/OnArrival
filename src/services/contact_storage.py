import json
from src.models.contact import Contact
from src.models.group import Group
import os
from pathlib import Path

class ContactStorage:
    def __init__(self, filename: str = 'contacts.json', groups_filename: str = 'groups.json'):
        # Get the base directory for data storage
        self.data_dir = self._get_data_directory()
        self.filename = os.path.join(self.data_dir, filename)
        self.groups_filename = os.path.join(self.data_dir, groups_filename)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_data_directory(self) -> str:
        """Get the appropriate data directory based on environment"""
        if 'PYTHONANYWHERE_DOMAIN' in os.environ:
            # PythonAnywhere environment
            username = os.getenv('USERNAME', 'defaultuser')
            return os.path.join('/home', username, 'onarrival', 'data')
        else:
            # Local development environment
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

    def load_contacts(self) -> list[Contact]:
        try:
            with open(self.filename, 'r') as f:
                contacts_data = json.load(f)
                return [Contact.from_dict(contact) for contact in contacts_data]
        except FileNotFoundError:
            return []

    def save_contacts(self, contacts: list[Contact]) -> None:
        with open(self.filename, 'w') as f:
            json.dump([contact.to_dict() for contact in contacts], f)

    def delete_contact(self, contact: Contact) -> None:
        contacts = self.load_contacts()
        contacts = [c for c in contacts if c.phone != contact.phone]
        self.save_contacts(contacts)

    def load_groups(self) -> list[Group]:
        try:
            with open(self.groups_filename, 'r') as f:
                groups_data = json.load(f)
                groups = []
                for group_data in groups_data:
                    contacts = [Contact.from_dict(contact) for contact in group_data.get('contacts', [])]
                    group = Group(
                        name=group_data['name'],
                        contacts=contacts
                    )
                    groups.append(group)
                return groups
        except FileNotFoundError:
            return []

    def save_groups(self, groups: list[Group]) -> None:
        groups_data = []
        for group in groups:
            group_data = {
                'name': group.name,
                'contacts': [contact.to_dict() for contact in group.contacts]
            }
            groups_data.append(group_data)
        
        with open(self.groups_filename, 'w') as f:
            json.dump(groups_data, f, indent=2)

    def add_group(self, group: Group) -> None:
        groups = self.load_groups()
        groups.append(group)
        self.save_groups(groups)

    def delete_group(self, group_name: str) -> None:
        groups = self.load_groups()
        groups = [g for g in groups if g.name != group_name]
        self.save_groups(groups)

    def update_group(self, group: Group) -> None:
        groups = self.load_groups()
        groups = [g for g in groups if g.name != group.name]
        groups.append(group)
        self.save_groups(groups) 