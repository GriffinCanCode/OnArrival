from typing import List, Optional, Tuple
from models.contact import Contact
from utils.validation import InputValidator, ValidationResult

class Group:
    def __init__(self, name: str, contacts: List[Contact] = None, validate: bool = True):
        if validate:
            # Validate group name
            name_result = InputValidator.validate_group_name(name)
            if not name_result.is_valid:
                raise ValueError(f"Invalid group name: {name_result.error_message}")
            
            self.name = name_result.sanitized_value
        else:
            # Skip validation (for loading from storage)
            self.name = name
        
        self.contacts = contacts or []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "contacts": [contact.to_dict() for contact in self.contacts]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Group':
        """Create group from dictionary without validation (for loading from storage)"""
        contacts = [Contact.from_dict(contact_data) for contact_data in data.get("contacts", [])]
        return cls(data["name"], contacts, validate=False)
    
    @classmethod
    def create_validated(cls, name: str) -> Tuple['Group', ValidationResult]:
        """Create a group with validation and return both group and validation result"""
        try:
            group = cls(name, validate=True)
            return group, ValidationResult(True, sanitized_value=f"Group created: {group.name}")
        except ValueError as e:
            return None, ValidationResult(False, str(e))
    
    def add_contact(self, contact: Contact) -> ValidationResult:
        """Add a contact to the group with validation"""
        if not isinstance(contact, Contact):
            return ValidationResult(False, "Invalid contact object")
        
        # Check for duplicate phone numbers
        if any(c.phone == contact.phone for c in self.contacts):
            return ValidationResult(False, f"Contact with phone number {contact.phone} already exists in group")
        
        # Check for duplicate names
        if any(c.name.lower() == contact.name.lower() for c in self.contacts):
            return ValidationResult(False, f"Contact with name '{contact.name}' already exists in group")
        
        self.contacts.append(contact)
        return ValidationResult(True, sanitized_value=f"Contact {contact.name} added to group {self.name}")
    
    def add_contact_by_details(self, name: str, phone: str) -> ValidationResult:
        """Add a contact by name and phone with validation"""
        contact, validation_result = Contact.create_validated(name, phone)
        
        if not validation_result.is_valid:
            return validation_result
        
        return self.add_contact(contact)
    
    def remove_contact(self, phone: str) -> ValidationResult:
        """Remove a contact by phone number"""
        original_count = len(self.contacts)
        self.contacts = [c for c in self.contacts if c.phone != phone]
        
        if len(self.contacts) == original_count:
            return ValidationResult(False, f"No contact found with phone number {phone}")
        
        return ValidationResult(True, sanitized_value=f"Contact removed from group {self.name}")
    
    def update_name(self, new_name: str) -> ValidationResult:
        """Update group name with validation"""
        name_result = InputValidator.validate_group_name(new_name)
        if name_result.is_valid:
            old_name = self.name
            self.name = name_result.sanitized_value
            return ValidationResult(True, sanitized_value=f"Group renamed from '{old_name}' to '{self.name}'")
        return name_result
    
    def find_contact_by_phone(self, phone: str) -> Optional[Contact]:
        """Find a contact by phone number"""
        return next((c for c in self.contacts if c.phone == phone), None)
    
    def find_contact_by_name(self, name: str) -> Optional[Contact]:
        """Find a contact by name (case insensitive)"""
        return next((c for c in self.contacts if c.name.lower() == name.lower()), None)
    
    def get_contact_count(self) -> int:
        """Get the number of contacts in the group"""
        return len(self.contacts)
    
    def is_empty(self) -> bool:
        """Check if the group has no contacts"""
        return len(self.contacts) == 0
    
    def validate_group_integrity(self) -> ValidationResult:
        """Validate the entire group for data integrity"""
        errors = []
        
        # Check for duplicate phone numbers
        phone_numbers = [c.phone for c in self.contacts]
        if len(phone_numbers) != len(set(phone_numbers)):
            errors.append("Group contains duplicate phone numbers")
        
        # Check for duplicate names (case insensitive)
        names = [c.name.lower() for c in self.contacts]
        if len(names) != len(set(names)):
            errors.append("Group contains duplicate contact names")
        
        # Validate each contact
        for i, contact in enumerate(self.contacts):
            try:
                # Try to create a new contact with the same data to validate
                Contact(contact.name, contact.phone, validate=True)
            except ValueError as e:
                errors.append(f"Contact {i+1} ({contact.name}) has invalid data: {str(e)}")
        
        if errors:
            return ValidationResult(False, "; ".join(errors))
        
        return ValidationResult(True, sanitized_value=f"Group {self.name} is valid with {len(self.contacts)} contacts")
    
    def __str__(self) -> str:
        return f"Group(name='{self.name}', contacts={len(self.contacts)})"
    
    def __repr__(self) -> str:
        return self.__str__()