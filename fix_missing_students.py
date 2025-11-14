#!/usr/bin/env python3
"""
Fix missing students in Students table
Adds students who have User_Role='Student' but are missing from Students table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import Config
import mysql.connector

def fix_missing_students():
    print("=" * 70)
    print("🔧 Fixing Missing Students in Students Table")
    print("=" * 70)
    print()
    
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = conn.cursor(dictionary=True)
        print("✅ Connected to database")
        print()
        
        # Find students in User table with User_Role='Student' but not in Students table
        query = """
            SELECT u.User_ID, u.Name, u.Email
            FROM User u
            WHERE u.User_Role = 'Student'
            AND u.User_ID NOT IN (SELECT User_ID FROM Students)
            ORDER BY u.User_ID
        """
        cursor.execute(query)
        missing_students = cursor.fetchall()
        
        if not missing_students:
            print("✅ All students are properly registered in Students table!")
            return
        
        print(f"⚠️  Found {len(missing_students)} students missing from Students table:")
        for student in missing_students:
            print(f"   - {student['Name']} (ID: {student['User_ID']})")
        print()
        
        # Add missing students to Students table
        print("📝 Adding missing students...")
        added_count = 0
        
        for student in missing_students:
            user_id = student['User_ID']
            name = student['Name']
            
            # Generate roll number (format: 10230XXX where XXX is User_ID)
            roll_no = f"10230{user_id:03d}"
            
            # Use a default class (101 - 1S01)
            class_id = 101
            
            # Generate parent email
            parent_email = f"parent.{name.lower().replace(' ', '')}@thapar.edu"
            
            try:
                insert_query = """
                    INSERT INTO Students (User_ID, Roll_no, Parent_Email, Class_ID)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        Roll_no = VALUES(Roll_no),
                        Parent_Email = VALUES(Parent_Email),
                        Class_ID = VALUES(Class_ID)
                """
                cursor.execute(insert_query, (user_id, roll_no, parent_email, class_id))
                conn.commit()
                print(f"   ✅ Added {name} (ID: {user_id}, Roll: {roll_no})")
                added_count += 1
            except Exception as e:
                print(f"   ❌ Error adding {name}: {e}")
        
        print()
        print("=" * 70)
        print(f"✅ Added {added_count} students to Students table")
        print("=" * 70)
        print()
        print("🔄 Restart the API to apply changes:")
        print("   docker-compose restart api")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    fix_missing_students()

