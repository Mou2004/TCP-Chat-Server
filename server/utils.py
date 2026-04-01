import logging
import json
import re

def setup_logger():
    """Configure and return the server logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('ChatServer')

def format_message(sender: str, content: str) -> str:
    """Format a message string for broadcasting."""
    return f"{sender}: {content}"

def validate_nickname(name: str) -> bool:
    """Validate a nickname based on length and characters."""
    if not name or len(name) < 2 or len(name) > 16:
        return False
    # Allow only letters, numbers, and underscores
    return re.match(r"^\w+$", name) is not None

def encode_json(data: dict) -> bytes:
    """Encode a dictionary to a JSON-formatted bytes object."""
    return (json.dumps(data) + "\n").encode('utf-8')

def decode_json(data: bytes) -> dict:
    """Decode a JSON-formatted bytes object to a dictionary."""
    try:
        return json.loads(data.decode('utf-8').strip())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
