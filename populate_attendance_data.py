#!/usr/bin/env python3
"""
Script to populate the database with sample attendance data
- Enrolls students in subjects
- Creates attendance sessions
- Marks attendance for students with varied percentages (some low, some high)
"""

import sys
import os
from datetime import datetime, date, time, timedelta
import random

# Add backend to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(script_dir, 'backend')

# Check if we're running in Docker container
if os.path.exists('/app/backend'):
    # Running in Docker
    backend_path = '/app/backend'
    sys.path.insert(0, backend_path)
else:
    # Running on host
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
    else:
        # Maybe we're already in backend directory
        backend_path = script_dir
        sys.path.insert(0, backend_path)

from database import DatabaseManager

def populate_attendance_data():
    """Populate database with sample attendance data"""
    db = DatabaseManager()
    
    try:
        print("🚀 Starting database population...")
        
        # Step 1: Enroll students in subjects
        print("\n📚 Step 1: Enrolling students in subjects...")
        
        # Get all students
        students_query = "SELECT User_ID, Class_ID FROM Students"
        students = db.execute_query(students_query, fetch=True) or []
        print(f"   Found {len(students)} students")
        
        # Get all subjects
        subjects_query = "SELECT Subject_ID, Class_ID FROM Subject"
        subjects = db.execute_query(subjects_query, fetch=True) or []
        print(f"   Found {len(subjects)} subjects")
        
        # Enroll students in subjects based on their class
        enrollments = []
        for student in students:
            student_class_id = student['Class_ID']
            # Find subjects for this class
            for subject in subjects:
                if subject['Class_ID'] == student_class_id:
                    enrollments.append((student['User_ID'], subject['Subject_ID']))
        
        # Insert enrollments (skip if already exists)
        enrollment_count = 0
        for user_id, subject_id in enrollments:
            try:
                db.execute_query(
                    "INSERT IGNORE INTO Student_Subject (User_ID, Subject_ID) VALUES (%s, %s)",
                    (user_id, subject_id)
                )
                enrollment_count += 1
            except Exception as e:
                print(f"   ⚠️  Error enrolling student {user_id} in subject {subject_id}: {e}")
        
        print(f"   ✅ Enrolled students in {enrollment_count} subject-student combinations")
        
        # Step 2: Create attendance sessions for the past 2 weeks
        print("\n📅 Step 2: Creating attendance sessions...")
        
        # Get subjects with their teachers
        subjects_with_teachers = db.execute_query(
            "SELECT Subject_ID, User_ID, Subject_Name FROM Subject",
            fetch=True
        ) or []
        
        session_count = 0
        today = date.today()
        
        # Create sessions for the past 14 days
        for day_offset in range(14, 0, -1):
            session_date = today - timedelta(days=day_offset)
            
            # Skip weekends (optional - you can remove this if you want weekend sessions)
            if session_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
            
            for subject in subjects_with_teachers:
                # Create 1-2 sessions per day per subject
                num_sessions = random.choice([1, 2])
                
                for session_num in range(num_sessions):
                    # Random time between 9 AM and 4 PM
                    start_hour = random.randint(9, 15)
                    start_minute = random.choice([0, 30])
                    start_time = time(start_hour, start_minute)
                    
                    # End time 1-2 hours later
                    end_hour = start_hour + random.choice([1, 2])
                    end_minute = start_minute
                    if end_hour >= 24:
                        end_hour = 23
                        end_minute = 59
                    end_time = time(end_hour, end_minute)
                    
                    # Session type
                    session_type = random.choice(['Lecture', 'Lab', 'Tutorial'])
                    
                    # Status: older sessions are Completed, recent ones might be Ongoing
                    if day_offset <= 1:
                        status = random.choice(['Scheduled', 'Ongoing', 'Completed'])
                    else:
                        status = 'Completed'
                    
                    try:
                        # Check if session already exists
                        existing = db.execute_query(
                            """SELECT Session_ID FROM Attendance_Session 
                               WHERE Subject_ID = %s AND Session_Date = %s AND Start_Time = %s""",
                            (subject['Subject_ID'], session_date, start_time),
                            fetch_one=True
                        )
                        
                        if not existing:
                            db.execute_query(
                                """INSERT INTO Attendance_Session 
                                   (Subject_ID, Session_Date, Start_Time, End_Time, Session_Type, Status, Created_By)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (subject['Subject_ID'], session_date, start_time, end_time, 
                                 session_type, status, subject['User_ID'])
                            )
                            session_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Error creating session: {e}")
        
        print(f"   ✅ Created {session_count} attendance sessions")
        
        # Step 3: Mark attendance for students
        print("\n✅ Step 3: Marking attendance for students...")
        
        # Get all completed sessions
        sessions = db.execute_query(
            "SELECT Session_ID, Subject_ID, Session_Date, Start_Time FROM Attendance_Session WHERE Status = 'Completed'",
            fetch=True
        ) or []
        
        print(f"   Found {len(sessions)} completed sessions")
        
        attendance_count = 0
        
        for session in sessions:
            session_id = session['Session_ID']
            subject_id = session['Subject_ID']
            session_date = session['Session_Date']
            session_start = session['Start_Time']
            
            # Convert session_start to time object if it's a timedelta
            if isinstance(session_start, timedelta):
                total_seconds = int(session_start.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                session_start = time(hours, minutes)
            elif isinstance(session_start, str):
                # Parse string time
                parts = session_start.split(':')
                session_start = time(int(parts[0]), int(parts[1]))
            
            # Get all students enrolled in this subject
            enrolled_students = db.execute_query(
                """SELECT ss.User_ID FROM Student_Subject ss
                   WHERE ss.Subject_ID = %s""",
                (subject_id,),
                fetch=True
            ) or []
            
            for student in enrolled_students:
                user_id = student['User_ID']
                
                # Check if already marked
                existing = db.execute_query(
                    "SELECT Attendance_ID FROM Attendance WHERE Session_ID = %s AND User_ID = %s",
                    (session_id, user_id),
                    fetch_one=True
                )
                
                if existing:
                    continue  # Skip if already marked
                
                # Randomly decide attendance status
                # 70% present, 15% late, 15% absent (to create varied percentages)
                rand = random.random()
                
                if rand < 0.70:
                    status = 'Present'
                elif rand < 0.85:
                    status = 'Late'
                else:
                    status = 'Absent'
                
                # Only mark if Present or Late (Absent means no record)
                if status in ['Present', 'Late']:
                    # Calculate check-in time
                    if status == 'Present':
                        # Arrived on time or slightly early
                        check_in_hour = session_start.hour
                        check_in_minute = session_start.minute + random.randint(-5, 5)
                    else:  # Late
                        # Arrived 10-30 minutes late
                        check_in_hour = session_start.hour
                        check_in_minute = session_start.minute + random.randint(10, 30)
                    
                    if check_in_minute >= 60:
                        check_in_hour += 1
                        check_in_minute -= 60
                    elif check_in_minute < 0:
                        check_in_hour -= 1
                        check_in_minute += 60
                    
                    check_in_time = datetime.combine(session_date, time(check_in_hour, check_in_minute))
                    
                    try:
                        db.execute_query(
                            """INSERT INTO Attendance 
                               (Session_ID, User_ID, Subject_ID, Date, Check_In_Time, Status, Marked_By)
                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (session_id, user_id, subject_id, session_date, check_in_time, status, 'Manual')
                        )
                        attendance_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Error marking attendance: {e}")
        
        print(f"   ✅ Marked {attendance_count} attendance records")
        
        # Step 4: Create some students with intentionally low attendance
        print("\n📉 Step 4: Creating low attendance scenarios...")
        
        # Get a few students and mark them absent for many sessions
        low_attendance_students = random.sample(enrolled_students, min(3, len(enrolled_students)))
        
        for student in low_attendance_students:
            user_id = student['User_ID']
            # Get their subjects
            student_subjects = db.execute_query(
                "SELECT Subject_ID FROM Student_Subject WHERE User_ID = %s",
                (user_id,),
                fetch=True
            ) or []
            
            for subj in student_subjects:
                subject_id = subj['Subject_ID']
                # Get sessions for this subject
                subject_sessions = [s for s in sessions if s['Subject_ID'] == subject_id]
                
                # Mark present for only 30-50% of sessions
                present_count = int(len(subject_sessions) * random.uniform(0.3, 0.5))
                present_sessions = random.sample(subject_sessions, present_count)
                
                for session in subject_sessions:
                    session_id = session['Session_ID']
                    
                    # Check if already marked
                    existing = db.execute_query(
                        "SELECT Attendance_ID FROM Attendance WHERE Session_ID = %s AND User_ID = %s",
                        (session_id, user_id),
                        fetch_one=True
                    )
                    
                    if existing:
                        continue
                    
                    if session in present_sessions:
                        # Mark as present
                        session_date = session['Session_Date']
                        session_start = session['Start_Time']
                        
                        # Convert session_start to time object if needed
                        if isinstance(session_start, timedelta):
                            total_seconds = int(session_start.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            session_start = time(hours, minutes)
                        elif isinstance(session_start, str):
                            parts = session_start.split(':')
                            session_start = time(int(parts[0]), int(parts[1]))
                        
                        check_in_time = datetime.combine(session_date, session_start)
                        
                        try:
                            db.execute_query(
                                """INSERT INTO Attendance 
                                   (Session_ID, User_ID, Subject_ID, Date, Check_In_Time, Status, Marked_By)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (session_id, user_id, subject_id, session_date, check_in_time, 'Present', 'Manual')
                            )
                        except Exception as e:
                            pass  # Ignore errors for existing records
        
        print("   ✅ Created low attendance scenarios")
        
        print("\n✅ Database population completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Enrollments: {enrollment_count}")
        print(f"   - Sessions: {session_count}")
        print(f"   - Attendance records: {attendance_count}")
        
    except Exception as e:
        print(f"\n❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = populate_attendance_data()
    sys.exit(0 if success else 1)

