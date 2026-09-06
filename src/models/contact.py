from utils.validation import InputValidator, ValidationResult
from typing import Dict, Tuple

class Contact:
    def __init__(self, name: str, phone: str, validate: bool = True):
        if validate:
            # Validate inputs during creation
            name_result = InputValidator.validate_contact_name(name)
            if not name_result.is_valid:
                raise ValueError(f"Invalid contact name: {name_result.error_message}")
            
            phone_result = InputValidator.validate_phone_number(phone)
            if not phone_result.is_valid:
                raise ValueError(f"Invalid phone number: {phone_result.error_message}")
            
            # Use sanitized values
            self.name = name_result.sanitized_value
            self.phone = phone_result.sanitized_value
        else:
            # Skip validation (for loading from storage)
            self.name = name
            self.phone = phone

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        """Create contact from dictionary without validation (for loading from storage)"""
        return cls(data["name"], data["phone"], validate=False)
    
    @classmethod
    def create_validated(cls, name: str, phone: str) -> Tuple['Contact', ValidationResult]:
        """Create a contact with validation and return both contact and validation result"""
        try:
            contact = cls(name, phone, validate=True)
            return contact, ValidationResult(True, sanitized_value=f"Contact created: {contact.name}")
        except ValueError as e:
            return None, ValidationResult(False, str(e))
    
    def update_name(self, new_name: str) -> ValidationResult:
        """Update contact name with validation"""
        name_result = InputValidator.validate_contact_name(new_name)
        if name_result.is_valid:
            self.name = name_result.sanitized_value
        return name_result
    
    def update_phone(self, new_phone: str) -> ValidationResult:
        """Update contact phone with validation"""
        phone_result = InputValidator.validate_phone_number(new_phone)
        if phone_result.is_valid:
            self.phone = phone_result.sanitized_value
        return phone_result
    
    def __str__(self) -> str:
        return f"Contact(name='{self.name}', phone='{self.phone}')"
    
    def __repr__(self) -> str:
        return self.__str__()