import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 with SHA-256"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${password_hash.hex()}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, password_hash = stored_password.split('$')
        provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return provided_hash.hex() == password_hash
    except ValueError:
        return False
