"""
Validation utilities for the chatbot application.
"""

import re
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, ValidationError
import logging


logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def __bool__(self):
        """Return validation status."""
        return self.is_valid


def validate_message_content(content: str) -> ValidationResult:
    """
    Validate chat message content.
    
    Args:
        content: Message content to validate
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not content:
        result.add_error("Message content cannot be empty")
        return result
    
    content = content.strip()
    
    if not content:
        result.add_error("Message content cannot be only whitespace")
        return result
    
    if len(content) > 4000:
        result.add_error("Message content exceeds maximum length of 4000 characters")
    
    if len(content) < 1:
        result.add_error("Message content must be at least 1 character")
    
    # Check for potentially harmful content
    suspicious_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript URLs
        r'data:text/html',  # Data URLs
        r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            result.add_warning("Message content contains potentially suspicious patterns")
            break
    
    return result


def validate_conversation_id(conversation_id: str) -> ValidationResult:
    """
    Validate conversation ID format.
    
    Args:
        conversation_id: Conversation ID to validate
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not conversation_id:
        result.add_error("Conversation ID cannot be empty")
        return result
    
    # Check format (should be like "conv_xxxxxxxxxxxx")
    if not re.match(r'^conv_[a-f0-9]{12}$', conversation_id):
        result.add_error("Invalid conversation ID format")
    
    return result


def validate_user_id(user_id: str) -> ValidationResult:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID to validate
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not user_id:
        result.add_error("User ID cannot be empty")
        return result
    
    # Check format and length
    if len(user_id) < 3:
        result.add_error("User ID must be at least 3 characters")
    
    if len(user_id) > 50:
        result.add_error("User ID cannot exceed 50 characters")
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        result.add_error("User ID can only contain letters, numbers, underscores, and hyphens")
    
    return result


def validate_model_parameters(params: Dict[str, Any]) -> ValidationResult:
    """
    Validate LLM model parameters.
    
    Args:
        params: Dictionary of model parameters
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not isinstance(params, dict):
        result.add_error("Model parameters must be a dictionary")
        return result
    
    # Validate temperature
    if 'temperature' in params:
        temp = params['temperature']
        if not isinstance(temp, (int, float)):
            result.add_error("Temperature must be a number")
        elif temp < 0 or temp > 2:
            result.add_error("Temperature must be between 0 and 2")
    
    # Validate max_tokens
    if 'max_tokens' in params:
        max_tokens = params['max_tokens']
        if not isinstance(max_tokens, int):
            result.add_error("Max tokens must be an integer")
        elif max_tokens < 1 or max_tokens > 4000:
            result.add_error("Max tokens must be between 1 and 4000")
    
    # Validate top_p
    if 'top_p' in params:
        top_p = params['top_p']
        if not isinstance(top_p, (int, float)):
            result.add_error("Top_p must be a number")
        elif top_p < 0 or top_p > 1:
            result.add_error("Top_p must be between 0 and 1")
    
    # Validate frequency_penalty
    if 'frequency_penalty' in params:
        freq_penalty = params['frequency_penalty']
        if not isinstance(freq_penalty, (int, float)):
            result.add_error("Frequency penalty must be a number")
        elif freq_penalty < -2 or freq_penalty > 2:
            result.add_error("Frequency penalty must be between -2 and 2")
    
    # Validate presence_penalty
    if 'presence_penalty' in params:
        pres_penalty = params['presence_penalty']
        if not isinstance(pres_penalty, (int, float)):
            result.add_error("Presence penalty must be a number")
        elif pres_penalty < -2 or pres_penalty > 2:
            result.add_error("Presence penalty must be between -2 and 2")
    
    # Validate model name
    if 'model' in params:
        model = params['model']
        valid_models = [
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
            'gpt-4',
            'gpt-4-32k',
            'gpt-4-turbo-preview'
        ]
        if model not in valid_models:
            result.add_warning(f"Model '{model}' may not be supported")
    
    return result


def validate_pydantic_model(model_class: BaseModel, data: Dict[str, Any]) -> ValidationResult:
    """
    Validate data against a Pydantic model.
    
    Args:
        model_class: Pydantic model class
        data: Data to validate
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    try:
        model_class(**data)
    except ValidationError as e:
        result.is_valid = False
        for error in e.errors():
            field = ' -> '.join(str(loc) for loc in error['loc'])
            message = error['msg']
            result.add_error(f"{field}: {message}")
    except Exception as e:
        result.add_error(f"Validation error: {str(e)}")
    
    return result


def validate_file_upload(
    file_content: bytes,
    allowed_extensions: List[str] = None,
    max_size_mb: int = 10
) -> ValidationResult:
    """
    Validate uploaded file.
    
    Args:
        file_content: File content as bytes
        allowed_extensions: List of allowed file extensions
        max_size_mb: Maximum file size in megabytes
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not file_content:
        result.add_error("File content is empty")
        return result
    
    # Check file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        result.add_error(f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)")
    
    # Basic file type validation could be added here
    # This would require additional libraries for proper file type detection
    
    return result


def sanitize_input(input_value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        input_value: Input string to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized input string
    """
    if not input_value:
        return ""
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', input_value)
    
    # Remove SQL injection patterns
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    ]
    
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_api_key(api_key: str) -> ValidationResult:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
    
    Returns:
        ValidationResult object
    """
    result = ValidationResult(True)
    
    if not api_key:
        result.add_error("API key cannot be empty")
        return result
    
    # Basic OpenAI API key format validation
    if api_key.startswith('sk-'):
        if len(api_key) < 20:
            result.add_error("API key appears to be too short")
    else:
        result.add_warning("API key format may be invalid (should start with 'sk-')")
    
    return result