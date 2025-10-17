"""
Utility functions for the chatbot application.
"""

import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging


logger = logging.getLogger(__name__)


def generate_conversation_id() -> str:
    """
    Generate a unique conversation ID.
    
    Returns:
        Unique conversation identifier
    """
    return f"conv_{uuid.uuid4().hex[:12]}"


def generate_message_id() -> str:
    """
    Generate a unique message ID.
    
    Returns:
        Unique message identifier
    """
    return f"msg_{uuid.uuid4().hex[:12]}"


def generate_user_id() -> str:
    """
    Generate a unique user ID.
    
    Returns:
        Unique user identifier
    """
    return f"user_{uuid.uuid4().hex[:8]}"


def sanitize_text(text: str, max_length: int = 4000) -> str:
    """
    Sanitize text input by removing unwanted characters and limiting length.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>&"]', '', text)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized


def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object (defaults to current UTC time)
        format_str: Format string for datetime
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.strftime(format_str)


def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a timestamp string to datetime object.
    
    Args:
        timestamp_str: Timestamp string
        format_str: Format string for parsing
    
    Returns:
        Parsed datetime object
    """
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError as e:
        logger.error(f"Error parsing timestamp {timestamp_str}: {str(e)}")
        return datetime.utcnow()


def calculate_token_estimate(text: str) -> int:
    """
    Estimate the number of tokens in a text.
    
    This is a rough approximation. For production use, consider using
    the tiktoken library for accurate token counting.
    
    Args:
        text: Input text
    
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Rough approximation: 1 token ≈ 4 characters for English text
    return max(1, len(text) // 4)


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """
    Generate a hash of the input text.
    
    Args:
        text: Input text to hash
        algorithm: Hashing algorithm (md5, sha1, sha256, etc.)
    
    Returns:
        Hexadecimal hash string
    """
    if not text:
        return ""
    
    try:
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode('utf-8'))
        return hash_obj.hexdigest()
    except ValueError:
        logger.error(f"Unsupported hash algorithm: {algorithm}")
        # Fallback to SHA256
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with optional suffix.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncating
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple word frequency.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords to return
    
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
    }
    
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequency and return most common
    word_count = {}
    for word in keywords:
        word_count[word] = word_count.get(word, 0) + 1
    
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and size_index < len(size_names) - 1:
        size /= 1024.0
        size_index += 1
    
    return f"{size:.1f} {size_names[size_index]}"


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing or replacing invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Cleaned filename
    """
    if not filename:
        return "untitled"
    
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Remove leading/trailing underscores and dots
    cleaned = cleaned.strip('_.')
    
    # Ensure it's not empty
    if not cleaned:
        cleaned = "untitled"
    
    return cleaned


def get_utc_timestamp() -> datetime:
    """
    Get current UTC timestamp.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate
    
    Returns:
        True if valid UUID, False otherwise
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False