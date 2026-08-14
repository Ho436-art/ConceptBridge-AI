"""
ConceptBridge AI - Security & Authentication Utilities
Handles salted, iterative password hashing to ensure no plaintext passwords are stored.
"""

import hashlib
import hmac
import secrets
from typing import Tuple


def hash_password(password: str, iterations: int = 100_000) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a cryptographically secure 16-byte salt.
    Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt.hex()}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a plain password against a stored PBKDF2 hash using constant-time comparison.
    """
    if not password or not stored_hash:
        return False

    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False

        algorithm, iterations_str, salt_hex, hash_hex = parts
        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(hash_hex)

        actual_key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=salt,
            iterations=iterations,
        )

        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False
