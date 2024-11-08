import json
from models.contact import Contact
from models.group import Group
import os
from pathlib import Path

class ContactStorage:
    def __init__(self):
        try:
            # Use a directory in /tmp which is writable by the web app
            self.data_dir = '/tmp/onarrival_data'
            self.contacts_file = os.path.join(self.data_dir, 'contacts.json')
            self.groups_filename = os.path.join(self.data_dir, 'groups.json')
            
            # Create the directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Initialize empty contacts file if it doesn't exist
            if not os.path.exists(self.contacts_file):
                with open(self.contacts_file, 'w') as f:
                    json.dump([], f)
                    
            # Initialize empty groups file if it doesn't exist
            if not os.path.exists(self.groups_filename):
                with open(self.groups_filename, 'w') as f:
                    json.dump([], f)
                    
        except Exception as e:
            print(f"Storage initialization error: {str(e)}")
            raise

    def load_contacts(self) -> list[Contact]:
        try:
            with open(self.contacts_file, 'r') as f:
                contacts_data = json.load(f)
                return [Contact.from_dict(contact) for contact in contacts_data]
        except FileNotFoundError:
            return []

    def save_contacts(self, contacts: list[Contact]) -> None:
        with open(self.contacts_file, 'w') as f:
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