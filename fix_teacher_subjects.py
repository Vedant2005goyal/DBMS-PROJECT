#!/usr/bin/env python3
"""
Fix teacher-subject assignments in the database
This script ensures all teachers have their subjects properly assigned
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import DatabaseManager
from backend.config import Config

def fix_teacher_subjects():
    """Fix teacher-subject assignments"""
    db = DatabaseManager()
    
    print("=" * 70)
    print("🔧 Fixing Teacher-Subject Assignments")
    print("=" * 70)
    print()
    
    # Step 1: Fix Faculty table
    print("📋 Step 1: Ensuring Faculty table has correct entries...")
    try:
        # Delete existing entries to avoid conflicts
        db.execute_query(
            "DELETE FROM Faculty WHERE User_ID IN (3, 7, 16, 18, 19)"
        )
        
        # Insert correct Faculty entries
        faculty_data = [
            (3, 'COE', 'Professor'),
            (7, 'ECE', 'Associate Professor'),
            (16, 'ME', 'Professor'),
            (18, 'COE', 'Faculty'),
            (19, 'COE', 'Faculty')
        ]
        
        for user_id, dept, role in faculty_data:
            db.execute_query(
                """INSERT INTO Faculty (User_ID, Department, Faculty_Role) 
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE 
                   Department = VALUES(Department),
                   Faculty_Role = VALUES(Faculty_Role)""",
                (user_id, dept, role)
            )
        
        print("✅ Faculty table updated")
    except Exception as e:
        print(f"⚠️  Error updating Faculty table: {e}")
    
    print()
    
    # Step 2: Ensure Class table has required entries
    print("📚 Step 2: Ensuring Class table has required entries...")
    try:
        classes_data = [
            (101, '1S01', 1, 'COE'),
            (102, '1S02', 1, 'COE'),
            (103, '2S01', 2, 'COE'),
            (104, '2S02', 2, 'COE'),
            (105, '3S01', 3, 'COE'),
            (106, '3S02', 3, 'COE'),
            (107, '4S01', 4, 'COE'),
            (108, '4S02', 4, 'COE'),
            (111, '1S03', 1, 'EEC'),
            (112, '1S04', 1, 'EEC'),
            (113, '2S03', 2, 'EEC'),
            (114, '3S03', 3, 'EEE'),
            (115, '4S03', 4, 'EEC'),
            (121, '1S05', 1, 'ME'),
            (122, '1S06', 1, 'ME'),
            (123, '2S04', 2, 'ME'),
            (124, '3S04', 3, 'ME'),
            (125, '4S04', 4, 'ME'),
            (131, '1S07', 1, 'CE'),
            (132, '2S05', 2, 'CE'),
            (133, '3S05', 3, 'CE'),
            (134, '4S05', 4, 'CE'),
        ]
        
        for class_id, class_name, year, dept in classes_data:
            db.execute_query(
                """INSERT INTO Class (Class_ID, Class_Name, Year, Department)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                   Class_Name = VALUES(Class_Name),
                   Year = VALUES(Year),
                   Department = VALUES(Department)""",
                (class_id, class_name, year, dept)
            )
        
        print(f"✅ {len(classes_data)} classes inserted/updated")
    except Exception as e:
        print(f"⚠️  Error updating classes: {e}")
    
    print()
    
    # Step 3: Insert/Update Subjects
    print("📚 Step 3: Ensuring all subjects are properly assigned...")
    try:
        subjects_data = [
            (1001, 'Introduction to Programming', 'UCS101', 3, 101, 4, 1),
            (1002, 'Basic Electrical Engineering', 'UES101', 7, 101, 3, 1),
            (1003, 'Physics', 'UPH101', 16, 101, 3, 2),
            (1005, 'Data Structures', 'UCS310', 3, 103, 4, 3),
            (1007, 'Operating Systems', 'UCS410', 3, 103, 4, 4),
            (1008, 'Computer Architecture', 'UCS411', 7, 103, 3, 4),
            (1009, 'Database Management Systems', 'UCS510', 16, 105, 3, 5),
            (1010, 'Software Engineering', 'UCS511', 3, 105, 3, 5),
            (1011, 'Computer Networks', 'UCS610', 16, 105, 4, 6),
            (1013, 'Machine Learning', 'UCS710', 7, 107, 3, 7),
            (1014, 'Capstone', 'UCS799', 16, 107, 4, 7),
            (1016, 'Basic Electronics', 'UEC101', 7, 111, 4, 1),
            (1018, 'Analog Electronics', 'UEC310', 7, 113, 3, 3),
            (1020, 'Communication Systems', 'UEC510', 7, 114, 3, 5),
            (1022, 'Engineering Drawing', 'UME101', 16, 121, 2, 1),
            (1024, 'Thermodynamics', 'UME310', 16, 123, 4, 3),
            (1026, 'Fluid Mechanics', 'UME510', 16, 124, 3, 5),
            (1027, 'Heat Transfer', 'UME610', 16, 124, 4, 6),
            (1028, 'Surveying', 'UCE310', 3, 132, 3, 3),
        ]
        
        for subj_id, name, code, user_id, class_id, credits, semester in subjects_data:
            db.execute_query(
                """INSERT INTO Subject 
                   (Subject_ID, Subject_Name, Subject_Code, User_ID, Class_ID, Credits, Semester)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                   Subject_Name = VALUES(Subject_Name),
                   Subject_Code = VALUES(Subject_Code),
                   User_ID = VALUES(User_ID),
                   Class_ID = VALUES(Class_ID),
                   Credits = VALUES(Credits),
                   Semester = VALUES(Semester)""",
                (subj_id, name, code, user_id, class_id, credits, semester)
            )
        
        print(f"✅ {len(subjects_data)} subjects inserted/updated")
    except Exception as e:
        print(f"⚠️  Error updating subjects: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Step 4: Verify assignments
    print("🔍 Step 4: Verifying teacher-subject assignments...")
    print()
    
    try:
        # Get teachers with their subject counts
        teachers = db.execute_query(
            """SELECT 
                f.User_ID,
                u.Name as Teacher_Name,
                u.Email,
                f.Department,
                COUNT(s.Subject_ID) as Subject_Count
            FROM Faculty f
            LEFT JOIN User u ON f.User_ID = u.User_ID
            LEFT JOIN Subject s ON f.User_ID = s.User_ID
            GROUP BY f.User_ID, u.Name, u.Email, f.Department
            ORDER BY f.User_ID""",
            fetch=True
        )
        
        print("📊 Teachers and their subjects:")
        print("-" * 70)
        for teacher in teachers:
            status = "✅" if teacher['Subject_Count'] > 0 else "❌"
            print(f"{status} {teacher['Teacher_Name']:25s} (ID: {teacher['User_ID']:2d}) - "
                  f"{teacher['Subject_Count']:2d} subjects - {teacher['Department']}")
        
        print()
        
        # Show subjects for each teacher
        for teacher_id in [3, 7, 16]:
            subjects = db.execute_query(
                """SELECT Subject_ID, Subject_Name, Subject_Code 
                   FROM Subject 
                   WHERE User_ID = %s 
                   ORDER BY Subject_Name""",
                (teacher_id,),
                fetch=True
            )
            
            if subjects:
                teacher_name = db.execute_query(
                    "SELECT Name FROM User WHERE User_ID = %s",
                    (teacher_id,),
                    fetch_one=True
                )
                name = teacher_name['Name'] if teacher_name else f"User {teacher_id}"
                print(f"👤 {name} (ID: {teacher_id}):")
                for subj in subjects:
                    print(f"   - {subj['Subject_Name']:40s} ({subj['Subject_Code']})")
                print()
        
    except Exception as e:
        print(f"⚠️  Error verifying: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 70)
    print("✅ Fix complete! Teachers should now have subjects assigned.")
    print("=" * 70)
    print()
    print("🔄 Next steps:")
    print("   1. Restart the API: docker-compose restart api")
    print("   2. Clear browser cache")
    print("   3. Login as a teacher and check subjects")

if __name__ == "__main__":
    try:
        fix_teacher_subjects()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

