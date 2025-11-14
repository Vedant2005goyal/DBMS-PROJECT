#!/usr/bin/env python3
"""
Quick script to check subjects in the database
Run this to verify subjects are properly assigned
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import DatabaseManager

def check_subjects():
    db = DatabaseManager()
    
    print("=" * 60)
    print("📚 Checking Subjects in Database")
    print("=" * 60)
    
    # Check all subjects
    all_subjects = db.execute_query(
        "SELECT Subject_ID, Subject_Name, Subject_Code, User_ID FROM Subject ORDER BY User_ID",
        fetch=True
    ) or []
    
    print(f"\n✅ Total subjects in database: {len(all_subjects)}")
    print("\n📋 All Subjects:")
    print("-" * 60)
    for subj in all_subjects:
        print(f"  ID: {subj['Subject_ID']:4d} | {subj['Subject_Name']:40s} | Teacher ID: {subj['User_ID']}")
    
    # Check subjects for specific teachers
    teachers = [3, 7, 16]
    print("\n" + "=" * 60)
    print("👨‍🏫 Subjects by Teacher")
    print("=" * 60)
    
    for teacher_id in teachers:
        teacher_info = db.execute_query(
            "SELECT Name, Email FROM User WHERE User_ID = %s",
            (teacher_id,),
            fetch_one=True
        )
        
        if teacher_info:
            teacher_name = teacher_info['Name']
            subjects = [s for s in all_subjects if s['User_ID'] == teacher_id]
            print(f"\n👤 {teacher_name} (ID: {teacher_id})")
            print(f"   Subjects: {len(subjects)}")
            for subj in subjects:
                print(f"     - {subj['Subject_Name']} ({subj['Subject_Code']})")
        else:
            print(f"\n❌ Teacher ID {teacher_id} not found in User table")
    
    # Check Faculty table
    print("\n" + "=" * 60)
    print("👨‍🏫 Faculty Table")
    print("=" * 60)
    faculty = db.execute_query(
        "SELECT f.User_ID, u.Name, f.Department, f.Faculty_Role FROM Faculty f LEFT JOIN User u ON f.User_ID = u.User_ID",
        fetch=True
    ) or []
    
    for fac in faculty:
        print(f"  ID: {fac['User_ID']:4d} | {fac['Name']:20s} | {fac['Department']:10s} | {fac['Faculty_Role']}")
    
    print("\n" + "=" * 60)
    print("✅ Check complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        check_subjects()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

