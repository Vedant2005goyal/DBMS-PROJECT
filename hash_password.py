#!/usr/bin/env python3
"""
Helper script to hash passwords for database insertion.
Usage: python hash_password.py <password>
"""
import hashlib
import sys

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hash_password.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = hash_password(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed}")
    print(f"\nSQL UPDATE example:")
    print(f"UPDATE User SET Password_Hash = '{hashed}' WHERE Email = 'your_email@example.com';")

