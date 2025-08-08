import re
import os
from urllib.parse import urlparse
import ipaddress

# Define a base directory for user data to prevent path traversal attacks
SAFE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'user_data'))

# Regex for simple alphanumeric names, allowing spaces, hyphens, and underscores
SIMPLE_NAME_REGEX = re.compile(r"^[a-zA-Z0-9\s_-]+$")

def is_valid_input(text: str, max_length: int = 255, regex: re.Pattern = SIMPLE_NAME_REGEX) -> bool:
    """
    Validates a generic string input against length and a regex pattern.
    """
    if len(text) > max_length:
        return False
    if not regex.match(text):
        return False
    return True

def is_valid_url(url: str) -> bool:
    """
    Validates a URL to ensure it is http/https and does not point to a private/internal IP address.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified:
                return False
        except ValueError:
            # Not an IP address, which is fine (it's a domain name)
            pass

    except Exception:
        return False

    return True

def is_safe_path(path: str) -> bool:
    """
    Validates if a given file path is within the allowed SAFE_BASE_DIR.
    """
    # Ensure the safe base directory exists
    if not os.path.exists(SAFE_BASE_DIR):
        os.makedirs(SAFE_BASE_DIR)

    # Normalize both paths to prevent traversal attacks (e.g., using '..')
    real_path = os.path.realpath(path)
    safe_dir_real = os.path.realpath(SAFE_BASE_DIR)

    return os.path.commonprefix([real_path, safe_dir_real]) == safe_dir_real

def get_safe_path(filename: str) -> str:
    """
    Returns a safe, absolute path for a given filename inside the SAFE_BASE_DIR.
    """
    return os.path.join(SAFE_BASE_DIR, filename)

def is_valid_cdp_url(url: str) -> bool:
    """
    Validates a CDP URL, allowing ws and wss schemes and localhost.
    """
    if not url:
        return False
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["ws", "wss"]:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # For CDP, we explicitly allow private/loopback addresses
        # but we can still check for a valid format
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            # It's a domain name, check if it's a valid looking one
            if not re.match(r"^[a-zA-Z0-9.-]+$", hostname):
                return False

    except Exception:
        return False

    return True
