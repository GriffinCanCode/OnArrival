import json
from models.contact import Contact
from models.group import Group
from utils.validation import InputValidator, ValidationResult
import os
from pathlib import Path
from typing import List, Optional, Tuple

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
                    
            # Validate existing data on startup
            self._validate_existing_data()
                    
        except Exception as e:
            print(f"Storage initialization error: {str(e)}")
            raise

    def _validate_existing_data(self):
        """Validate existing data and repair/clean if necessary"""
        try:
            # Validate and clean contacts
            contacts = self.load_contacts()
            cleaned_contacts = []
            
            for contact in contacts:
                try:
                    # Try to create a new contact to validate
                    validated_contact = Contact(contact.name, contact.phone, validate=True)
                    cleaned_contacts.append(validated_contact)
                except ValueError as e:
                    print(f"Warning: Removing invalid contact {contact.name} ({contact.phone}): {e}")
            
            if len(cleaned_contacts) != len(contacts):
                print(f"Cleaned {len(contacts) - len(cleaned_contacts)} invalid contacts")
                self.save_contacts(cleaned_contacts)
            
            # Validate and clean groups
            groups = self.load_groups()
            cleaned_groups = []
            
            for group in groups:
                validation_result = group.validate_group_integrity()
                if validation_result.is_valid:
                    cleaned_groups.append(group)
                else:
                    print(f"Warning: Group '{group.name}' has issues: {validation_result.error_message}")
                    # Try to repair the group by removing invalid contacts
                    repaired_group = self._repair_group(group)
                    if repaired_group:
                        cleaned_groups.append(repaired_group)
            
            if len(cleaned_groups) != len(groups):
                print(f"Cleaned {len(groups) - len(cleaned_groups)} invalid groups")
                self.save_groups(cleaned_groups)
                
        except Exception as e:
            print(f"Warning: Data validation failed: {e}")

    def _repair_group(self, group: Group) -> Optional[Group]:
        """Try to repair a group by removing invalid contacts"""
        try:
            valid_contacts = []
            
            for contact in group.contacts:
                try:
                    # Validate contact
                    Contact(contact.name, contact.phone, validate=True)
                    valid_contacts.append(contact)
                except ValueError:
                    print(f"Removing invalid contact {contact.name} from group {group.name}")
            
            if valid_contacts:
                # Create a new group with valid contacts
                repaired_group = Group(group.name, validate=False)
                repaired_group.contacts = valid_contacts
                return repaired_group
            else:
                print(f"Group {group.name} has no valid contacts, removing")
                return None
                
        except Exception:
            return None

    def load_contacts(self) -> List[Contact]:
        """Load contacts from storage"""
        try:
            with open(self.contacts_file, 'r') as f:
                contacts_data = json.load(f)
                return [Contact.from_dict(contact) for contact in contacts_data]
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading contacts: {e}")
            return []

    def save_contacts(self, contacts: List[Contact]) -> ValidationResult:
        """Save contacts to storage with validation"""
        try:
            # Validate all contacts before saving
            for contact in contacts:
                if not isinstance(contact, Contact):
                    return ValidationResult(False, "Invalid contact object in list")
            
            # Check for duplicates
            phone_numbers = [c.phone for c in contacts]
            if len(phone_numbers) != len(set(phone_numbers)):
                return ValidationResult(False, "Duplicate phone numbers detected")
            
            with open(self.contacts_file, 'w') as f:
                json.dump([contact.to_dict() for contact in contacts], f, indent=2)
            
            return ValidationResult(True, sanitized_value=f"Successfully saved {len(contacts)} contacts")
            
        except Exception as e:
            return ValidationResult(False, f"Failed to save contacts: {str(e)}")

    def add_contact(self, name: str, phone: str) -> ValidationResult:
        """Add a new contact with validation"""
        # Create contact with validation
        contact, validation_result = Contact.create_validated(name, phone)
        
        if not validation_result.is_valid:
            return validation_result
        
        # Load existing contacts
        contacts = self.load_contacts()
        
        # Check for duplicates
        if any(c.phone == contact.phone for c in contacts):
            return ValidationResult(False, f"Contact with phone number {contact.phone} already exists")
        
        if any(c.name.lower() == contact.name.lower() for c in contacts):
            return ValidationResult(False, f"Contact with name '{contact.name}' already exists")
        
        # Add contact and save
        contacts.append(contact)
        save_result = self.save_contacts(contacts)
        
        if save_result.is_valid:
            return ValidationResult(True, sanitized_value=f"Contact {contact.name} added successfully")
        else:
            return save_result

    def update_contact(self, old_phone: str, new_name: str, new_phone: str) -> ValidationResult:
        """Update an existing contact with validation"""
        contacts = self.load_contacts()
        
        # Find the contact to update
        contact_to_update = None
        for contact in contacts:
            if contact.phone == old_phone:
                contact_to_update = contact
                break
        
        if not contact_to_update:
            return ValidationResult(False, f"Contact with phone {old_phone} not found")
        
        # Validate new values
        name_result = InputValidator.validate_contact_name(new_name)
        if not name_result.is_valid:
            return ValidationResult(False, f"Invalid name: {name_result.error_message}")
        
        phone_result = InputValidator.validate_phone_number(new_phone)
        if not phone_result.is_valid:
            return ValidationResult(False, f"Invalid phone: {phone_result.error_message}")
        
        # Check for duplicates (excluding the current contact)
        for contact in contacts:
            if contact != contact_to_update:
                if contact.phone == phone_result.sanitized_value:
                    return ValidationResult(False, f"Phone number {phone_result.sanitized_value} already exists")
                if contact.name.lower() == name_result.sanitized_value.lower():
                    return ValidationResult(False, f"Contact name '{name_result.sanitized_value}' already exists")
        
        # Update the contact
        contact_to_update.name = name_result.sanitized_value
        contact_to_update.phone = phone_result.sanitized_value
        
        # Save contacts
        save_result = self.save_contacts(contacts)
        
        if save_result.is_valid:
            return ValidationResult(True, sanitized_value=f"Contact updated successfully")
        else:
            return save_result

    def delete_contact(self, contact: Contact) -> ValidationResult:
        """Delete a contact with validation"""
        try:
            contacts = self.load_contacts()
            original_count = len(contacts)
            
            # Remove contact
            contacts = [c for c in contacts if c.phone != contact.phone]
            
            if len(contacts) == original_count:
                return ValidationResult(False, f"Contact {contact.name} not found")
            
            # Also remove from all groups
            groups = self.load_groups()
            for group in groups:
                group.contacts = [c for c in group.contacts if c.phone != contact.phone]
            
            # Save both contacts and groups
            contact_save_result = self.save_contacts(contacts)
            if not contact_save_result.is_valid:
                return contact_save_result
            
            group_save_result = self.save_groups(groups)
            if not group_save_result.is_valid:
                return group_save_result
            
            return ValidationResult(True, sanitized_value=f"Contact {contact.name} deleted successfully")
            
        except Exception as e:
            return ValidationResult(False, f"Failed to delete contact: {str(e)}")

    def load_groups(self) -> List[Group]:
        """Load groups from storage"""
        try:
            with open(self.groups_filename, 'r') as f:
                groups_data = json.load(f)
                return [Group.from_dict(group_data) for group_data in groups_data]
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading groups: {e}")
            return []

    def save_groups(self, groups: List[Group]) -> ValidationResult:
        """Save groups to storage with validation"""
        try:
            # Validate all groups before saving
            for group in groups:
                if not isinstance(group, Group):
                    return ValidationResult(False, "Invalid group object in list")
                
                validation_result = group.validate_group_integrity()
                if not validation_result.is_valid:
                    return ValidationResult(False, f"Group '{group.name}' is invalid: {validation_result.error_message}")
            
            # Check for duplicate group names
            group_names = [g.name.lower() for g in groups]
            if len(group_names) != len(set(group_names)):
                return ValidationResult(False, "Duplicate group names detected")
            
            with open(self.groups_filename, 'w') as f:
                json.dump([group.to_dict() for group in groups], f, indent=2)
            
            return ValidationResult(True, sanitized_value=f"Successfully saved {len(groups)} groups")
            
        except Exception as e:
            return ValidationResult(False, f"Failed to save groups: {str(e)}")

    def add_group(self, name: str) -> ValidationResult:
        """Add a new group with validation"""
        # Create group with validation
        group, validation_result = Group.create_validated(name)
        
        if not validation_result.is_valid:
            return validation_result
        
        # Load existing groups
        groups = self.load_groups()
        
        # Check for duplicates
        if any(g.name.lower() == group.name.lower() for g in groups):
            return ValidationResult(False, f"Group with name '{group.name}' already exists")
        
        # Add group and save
        groups.append(group)
        save_result = self.save_groups(groups)
        
        if save_result.is_valid:
            return ValidationResult(True, sanitized_value=f"Group '{group.name}' created successfully")
        else:
            return save_result

    def delete_group(self, group_name: str) -> ValidationResult:
        """Delete a group with validation"""
        try:
            groups = self.load_groups()
            original_count = len(groups)
            
            # Remove group
            groups = [g for g in groups if g.name.lower() != group_name.lower()]
            
            if len(groups) == original_count:
                return ValidationResult(False, f"Group '{group_name}' not found")
            
            # Save groups
            save_result = self.save_groups(groups)
            
            if save_result.is_valid:
                return ValidationResult(True, sanitized_value=f"Group '{group_name}' deleted successfully")
            else:
                return save_result
                
        except Exception as e:
            return ValidationResult(False, f"Failed to delete group: {str(e)}")

    def update_group(self, group: Group) -> ValidationResult:
        """Update an existing group with validation"""
        try:
            # Validate the group
            validation_result = group.validate_group_integrity()
            if not validation_result.is_valid:
                return validation_result
            
            groups = self.load_groups()
            
            # Find and update the group
            for i, existing_group in enumerate(groups):
                if existing_group.name.lower() == group.name.lower():
                    groups[i] = group
                    break
            else:
                return ValidationResult(False, f"Group '{group.name}' not found")
            
            # Save groups
            save_result = self.save_groups(groups)
            
            if save_result.is_valid:
                return ValidationResult(True, sanitized_value=f"Group '{group.name}' updated successfully")
            else:
                return save_result
                
        except Exception as e:
            return ValidationResult(False, f"Failed to update group: {str(e)}")

    def add_contact_to_group(self, group_name: str, contact_name: str, contact_phone: str) -> ValidationResult:
        """Add a contact to a group with validation"""
        try:
            # Load groups
            groups = self.load_groups()
            
            # Find the group
            target_group = None
            for group in groups:
                if group.name.lower() == group_name.lower():
                    target_group = group
                    break
            
            if not target_group:
                return ValidationResult(False, f"Group '{group_name}' not found")
            
            # Add contact to group with validation
            add_result = target_group.add_contact_by_details(contact_name, contact_phone)
            if not add_result.is_valid:
                return add_result
            
            # Save groups
            save_result = self.save_groups(groups)
            
            if save_result.is_valid:
                return ValidationResult(True, sanitized_value=f"Contact added to group '{group_name}' successfully")
            else:
                return save_result
                
        except Exception as e:
            return ValidationResult(False, f"Failed to add contact to group: {str(e)}")

    def remove_contact_from_group(self, group_name: str, contact_phone: str) -> ValidationResult:
        """Remove a contact from a group with validation"""
        try:
            groups = self.load_groups()
            
            # Find the group
            target_group = None
            for group in groups:
                if group.name.lower() == group_name.lower():
                    target_group = group
                    break
            
            if not target_group:
                return ValidationResult(False, f"Group '{group_name}' not found")
            
            # Remove contact from group
            remove_result = target_group.remove_contact(contact_phone)
            if not remove_result.is_valid:
                return remove_result
            
            # Save groups
            save_result = self.save_groups(groups)
            
            if save_result.is_valid:
                return ValidationResult(True, sanitized_value=f"Contact removed from group '{group_name}' successfully")
            else:
                return save_result
                
        except Exception as e:
            return ValidationResult(False, f"Failed to remove contact from group: {str(e)}")

    def get_group_by_name(self, name: str) -> Optional[Group]:
        """Get a group by name"""
        groups = self.load_groups()
        return next((g for g in groups if g.name.lower() == name.lower()), None)

    def get_contact_by_phone(self, phone: str) -> Optional[Contact]:
        """Get a contact by phone number"""
        contacts = self.load_contacts()
        return next((c for c in contacts if c.phone == phone), None)

    def validate_storage_integrity(self) -> ValidationResult:
        """Validate the integrity of all stored data"""
        try:
            errors = []
            
            # Validate contacts
            contacts = self.load_contacts()
            phone_numbers = [c.phone for c in contacts]
            if len(phone_numbers) != len(set(phone_numbers)):
                errors.append("Duplicate phone numbers in contacts")
            
            # Validate groups
            groups = self.load_groups()
            group_names = [g.name.lower() for g in groups]
            if len(group_names) != len(set(group_names)):
                errors.append("Duplicate group names")
            
            for group in groups:
                group_validation = group.validate_group_integrity()
                if not group_validation.is_valid:
                    errors.append(f"Group '{group.name}': {group_validation.error_message}")
            
            if errors:
                return ValidationResult(False, "; ".join(errors))
            
            return ValidationResult(True, sanitized_value=f"Storage integrity verified: {len(contacts)} contacts, {len(groups)} groups")
            
        except Exception as e:
            return ValidationResult(False, f"Storage integrity check failed: {str(e)}") 