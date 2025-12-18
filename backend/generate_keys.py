#!/usr/bin/env python3
"""
Script to generate secure secret keys for Flask application.
Run this script to generate new SECRET_KEY and JWT_SECRET_KEY values.
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_hex_key(length=32):
    """Generate a hex-encoded secret key."""
    return secrets.token_hex(length)

if __name__ == "__main__":
    print("Generated Secret Keys:")
    print("=" * 50)
    print(f"SECRET_KEY={generate_hex_key(32)}")
    print(f"JWT_SECRET_KEY={generate_hex_key(32)}")
    print("=" * 50)
    print("\nCopy these values to your .env file")
    print("Make sure to keep these keys secure and never share them!")