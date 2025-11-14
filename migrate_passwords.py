#!/usr/bin/env python3
"""
Script to migrate plain text passwords to hashed passwords in the database.
Run this if you want to convert your database to use hashed passwords.

Usage:
    python migrate_passwords.py

Make sure to update api.py login function to hash passwords after running this.
"""
import hashlib
import mysql.connector
from config import Config
import sys

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_passwords():
    """Migrate all plain text passwords to hashed passwords"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get all users with plain text passwords
        cursor.execute("SELECT User_ID, Email, Password_Hash FROM User")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"Found {len(users)} users. Migrating passwords...")
        
        updated = 0
        for user in users:
            user_id = user['User_ID']
            email = user['Email']
            current_password = user['Password_Hash']
            
            # Check if password is already hashed (64 chars for SHA256)
            if len(current_password) == 64 and all(c in '0123456789abcdef' for c in current_password.lower()):
                print(f"  User {email} already has hashed password, skipping...")
                continue
            
            # Hash the password
            hashed_password = hash_password(current_password)
            
            # Update in database
            update_cursor = conn.cursor()
            update_cursor.execute(
                "UPDATE User SET Password_Hash = %s WHERE User_ID = %s",
                (hashed_password, user_id)
            )
            update_cursor.close()
            updated += 1
            print(f"  ✓ Updated password for {email}")
        
        conn.commit()
        print(f"\n✓ Migration complete! Updated {updated} passwords.")
        print("\n⚠ IMPORTANT: After migration, update api.py login function to hash passwords!")
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("=== Password Migration Script ===")
    print("This will convert plain text passwords to SHA256 hashed passwords.")
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_passwords()
    else:
        print("Migration cancelled.")

