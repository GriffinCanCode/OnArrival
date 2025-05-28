import re
import html
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    error_message: Optional[str] = None
    sanitized_value: Optional[str] = None

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Phone number patterns for different formats
    E164_PATTERN = re.compile(r'^\+[1-9]\d{1,14}$')
    US_PHONE_PATTERN = re.compile(r'^(\+1|1)?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
    
    # Name validation patterns
    NAME_PATTERN = re.compile(r'^[a-zA-Z\s\-\'\.]{1,50}$')
    BUSINESS_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\'\.&,]{1,100}$')
    
    # Message length limits
    MAX_MESSAGE_LENGTH = 1600  # SMS limit
    MAX_BUSINESS_NAME_LENGTH = 100
    MAX_CONTACT_NAME_LENGTH = 50
    
    @classmethod
    def validate_phone_number(cls, phone: str) -> ValidationResult:
        """
        Validate and normalize phone number to E.164 format
        Supports US and international formats
        """
        if not phone:
            return ValidationResult(False, "Phone number is required")
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone.strip())
        
        if not cleaned:
            return ValidationResult(False, "Invalid phone number format")
        
        # Check if already in E.164 format
        if cls.E164_PATTERN.match(cleaned):
            return ValidationResult(True, sanitized_value=cleaned)
        
        # Try to parse as US number
        us_match = cls.US_PHONE_PATTERN.match(phone.strip())
        if us_match:
            # Extract digits and format as E.164
            digits = re.sub(r'[^\d]', '', phone)
            if len(digits) == 10:
                # Add US country code
                e164_number = f"+1{digits}"
            elif len(digits) == 11 and digits.startswith('1'):
                # Already has country code
                e164_number = f"+{digits}"
            else:
                return ValidationResult(False, "Invalid US phone number format")
            
            return ValidationResult(True, sanitized_value=e164_number)
        
        # If starts with + but doesn't match E.164, it might be invalid
        if cleaned.startswith('+'):
            return ValidationResult(False, "Invalid international phone number format")
        
        # Try adding + and check if it becomes valid
        with_plus = f"+{cleaned}"
        if cls.E164_PATTERN.match(with_plus):
            return ValidationResult(True, sanitized_value=with_plus)
        
        return ValidationResult(False, "Invalid phone number format. Use format: +1234567890")
    
    @classmethod
    def validate_contact_name(cls, name: str) -> ValidationResult:
        """Validate contact name"""
        if not name:
            return ValidationResult(False, "Contact name is required")
        
        name = name.strip()
        
        if len(name) > cls.MAX_CONTACT_NAME_LENGTH:
            return ValidationResult(False, f"Contact name must be {cls.MAX_CONTACT_NAME_LENGTH} characters or less")
        
        if not cls.NAME_PATTERN.match(name):
            return ValidationResult(False, "Contact name contains invalid characters. Use only letters, spaces, hyphens, apostrophes, and periods")
        
        # Sanitize: remove extra spaces, proper case
        sanitized = ' '.join(name.split())
        sanitized = html.escape(sanitized)
        
        return ValidationResult(True, sanitized_value=sanitized)
    
    @classmethod
    def validate_business_name(cls, name: str) -> ValidationResult:
        """Validate business name"""
        if not name:
            return ValidationResult(False, "Business name is required")
        
        name = name.strip()
        
        if len(name) > cls.MAX_BUSINESS_NAME_LENGTH:
            return ValidationResult(False, f"Business name must be {cls.MAX_BUSINESS_NAME_LENGTH} characters or less")
        
        if not cls.BUSINESS_NAME_PATTERN.match(name):
            return ValidationResult(False, "Business name contains invalid characters")
        
        # Sanitize: remove extra spaces, escape HTML
        sanitized = ' '.join(name.split())
        sanitized = html.escape(sanitized)
        
        return ValidationResult(True, sanitized_value=sanitized)
    
    @classmethod
    def validate_message(cls, message: str) -> ValidationResult:
        """Validate message content"""
        if not message:
            return ValidationResult(False, "Message is required")
        
        message = message.strip()
        
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            return ValidationResult(False, f"Message must be {cls.MAX_MESSAGE_LENGTH} characters or less")
        
        # Check for potentially harmful content
        suspicious_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript URLs
            r'vbscript:',               # VBScript URLs
            r'onload\s*=',              # Event handlers
            r'onerror\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return ValidationResult(False, "Message contains potentially harmful content")
        
        # Sanitize: escape HTML and normalize whitespace
        sanitized = html.escape(message)
        # Normalize line breaks and spaces
        sanitized = re.sub(r'\s+', ' ', sanitized.replace('\n', ' ').replace('\r', ''))
        
        return ValidationResult(True, sanitized_value=sanitized)
    
    @classmethod
    def validate_group_name(cls, name: str) -> ValidationResult:
        """Validate group name"""
        if not name:
            return ValidationResult(False, "Group name is required")
        
        name = name.strip()
        
        if len(name) > 50:
            return ValidationResult(False, "Group name must be 50 characters or less")
        
        if not re.match(r'^[a-zA-Z0-9\s\-_]{1,50}$', name):
            return ValidationResult(False, "Group name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        # Sanitize
        sanitized = ' '.join(name.split())
        sanitized = html.escape(sanitized)
        
        return ValidationResult(True, sanitized_value=sanitized)
    
    @classmethod
    def validate_timer_minutes(cls, minutes: int) -> ValidationResult:
        """Validate timer duration in minutes"""
        if not isinstance(minutes, int):
            return ValidationResult(False, "Timer must be a number")
        
        if minutes < 1 or minutes > 120:
            return ValidationResult(False, "Timer must be between 1 and 120 minutes")
        
        return ValidationResult(True, sanitized_value=str(minutes))

class SecurityValidator:
    """Additional security validations"""
    
    # Rate limiting tracking (simple in-memory for now)
    _rate_limits = {}
    
    @classmethod
    def check_rate_limit(cls, identifier: str, max_requests: int = 10, window_minutes: int = 5) -> bool:
        """
        Simple rate limiting check
        Returns True if request is allowed, False if rate limit exceeded
        """
        import time
        
        current_time = time.time()
        window_seconds = window_minutes * 60
        
        if identifier not in cls._rate_limits:
            cls._rate_limits[identifier] = []
        
        # Clean old requests outside the window
        cls._rate_limits[identifier] = [
            req_time for req_time in cls._rate_limits[identifier]
            if current_time - req_time < window_seconds
        ]
        
        # Check if limit exceeded
        if len(cls._rate_limits[identifier]) >= max_requests:
            return False
        
        # Add current request
        cls._rate_limits[identifier].append(current_time)
        return True
    
    @classmethod
    def validate_request_size(cls, data: dict, max_size_kb: int = 50) -> ValidationResult:
        """Validate request payload size"""
        import json
        
        try:
            size_bytes = len(json.dumps(data).encode('utf-8'))
            size_kb = size_bytes / 1024
            
            if size_kb > max_size_kb:
                return ValidationResult(False, f"Request too large ({size_kb:.1f}KB). Maximum allowed: {max_size_kb}KB")
            
            return ValidationResult(True)
        except Exception:
            return ValidationResult(False, "Invalid request format") 