import logging
import json

def setup_logging(log_file: str = 'server.log') -> logging.Logger:
    """Initialize and configure logging for the console and file."""
    pass

def format_message(message_type: str, payload: dict) -> bytes:
    """Format dictionary into a JSON encoded byte string with a newline terminator."""
    pass

def parse_message(data: bytes) -> dict:
    """Parse JSON encoded bytes into a Python dictionary."""
    pass
