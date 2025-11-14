# Mark_Attendance.py

import face_recognition
import cv2 as cv
import os 
import mysql.connector
import numpy as np
import json
from datetime import datetime, date, time, timedelta
from config import Config  # <-- IMPORT CONFIG

class MarkAttendance:
    def __init__(self):
        try:
            # --- USE CONFIG FOR CREDENTIALS ---
            self.mysql_connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            self.cursor = self.mysql_connection.cursor(dictionary=True)
            print('MarkAttendance: Database connected successfully!!')
        except mysql.connector.Error as err:
            print(f"MarkAttendance: Database connection failed: {err}")
            raise

        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        try:
            query = "SELECT f.User_ID, u.Name, f.Face_Encoding FROM Face_Embeddings f JOIN User u ON f.User_ID = u.User_ID"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if not results:
                print("⚠️ WARNING: No faces registered in database! Face recognition will not work.")
                print("   Please register student faces using the face registration endpoint.")
                return
            
            for row in results:
                User_ID = row['User_ID']
                Name = row['Name']
                Encoding_json = row['Face_Encoding']
                
                try:
                    encoding_list = json.loads(Encoding_json)
                    encoding = np.array(encoding_list)

                    self.known_face_encodings.append(encoding)
                    self.known_face_ids.append(User_ID)
                    self.known_face_names.append(Name)
                except Exception as e:
                    print(f"⚠️ Error loading face encoding for {Name} (ID: {User_ID}): {e}")
                    continue
                    
            print(f"✓ Loaded {len(self.known_face_encodings)} registered faces:")
            for i, name in enumerate(self.known_face_names):
                print(f"   - {name} (ID: {self.known_face_ids[i]})")
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
            import traceback
            traceback.print_exc()
            
    
    # --- THIS IS THE NEW FUNCTION FOR YOUR API ---
    def mark_attendance_from_frame(self, frame, subject_id, session_id=None):
        """
        Recognizes a face from a single frame, finds the active session
        for the given subject_id, and marks attendance.
        If session_id is provided, use that session directly.
        """
        
        # 1. Find active session
        if session_id:
            # Use provided session_id, verify it exists and is active
            # First check if session exists
            query = """
                SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, Status
                FROM Attendance_Session
                WHERE Session_ID = %s
            """
            self.cursor.execute(query, (session_id,))
            session = self.cursor.fetchone()
            if not session:
                print(f"❌ Session ID {session_id} not found in database")
                return {'success': False, 'message': f'Session ID {session_id} not found'}
            
            # Check if subject_id matches (if provided)
            if subject_id and session['Subject_ID'] != subject_id:
                print(f"⚠️ Session {session_id} belongs to Subject {session['Subject_ID']}, but {subject_id} was provided")
                # Still allow it, but log a warning
            
            if session['Status'] not in ('Scheduled', 'Ongoing'):
                print(f"⚠️ Session {session_id} status is '{session['Status']}', not active")
                return {'success': False, 'message': f"Session status is '{session['Status']}', not active"}
            
            print(f"✓ Using session {session_id} for subject {session['Subject_ID']}")
            subject_id = session['Subject_ID']  # Use the session's subject_id
        else:
            # Find active session automatically
            sessions = self.get_active_session(Subject_ID=subject_id)
            if not sessions:
                return {'success': False, 'message': 'No active session found for this subject'}
            session = sessions[0]  # Use the first active session
            session_id = session['Session_ID']
        
        # 2. Resize frame for faster processing
        small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)

        # 3. Find faces in the frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        if not face_encodings:
            return {'success': False, 'message': 'No face detected in image. Please ensure your face is clearly visible.'}

        # 4. Use the first face found
        face_encoding = face_encodings[0]
        print(f"✓ Face detected, checking against {len(self.known_face_encodings)} registered faces...")
        
        name = "Unknown"
        User_ID = None

        if len(self.known_face_encodings) == 0:
            print("⚠️ No faces registered in database! Please register faces first.")
            return {'success': False, 'message': 'No faces registered in system. Please contact administrator to register your face.'}

        matches = face_recognition.compare_faces(
            self.known_face_encodings, face_encoding, tolerance=Config.FACE_RECOGNITION_TOLERANCE
        )
        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        
        print(f"Best match distance: {face_distances[best_match_index]:.4f}, threshold: {Config.FACE_RECOGNITION_TOLERANCE}")
        
        if matches[best_match_index] and face_distances[best_match_index] < Config.FACE_RECOGNITION_TOLERANCE:
            name = self.known_face_names[best_match_index]
            User_ID = self.known_face_ids[best_match_index]
            print(f"✓ Recognized: {name} (ID: {User_ID})")

        # 5. If face recognized, mark attendance
        if User_ID:
            print(f"📝 Marking attendance for {name} (ID: {User_ID}) in session {session_id}...")
            mark_success, message = self.mark_attendance(User_ID, name, session_id, subject_id)
            if mark_success:
                return {'success': True, 'name': name, 'message': message}
            else:
                return {'success': False, 'name': name, 'message': message}
        else:
            distance = face_distances[best_match_index] if len(face_distances) > 0 else 1.0
            print(f"❌ Face not recognized. Best match distance: {distance:.4f} (threshold: {Config.FACE_RECOGNITION_TOLERANCE})")
            return {'success': False, 'message': f'Face not recognized. Please ensure your face is registered. (Match distance: {distance:.3f})'}


    def get_buffer_time(self):
        # ... (Your existing function seems fine, but should use Config default) ...
        try:
            query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'session_buffer_minutes'"
            self.cursor.execute(query)
            setting = self.cursor.fetchone()

            if setting:
                buffer_minutes = int(setting['Setting_Value'])
            else:
                buffer_minutes = Config.SESSION_BUFFER_MINUTES # Use Config default
                insert_query = """
                    INSERT INTO Attendance_Settings (Setting_Key, Setting_Value, Description)
                    VALUES ('session_buffer_minutes', %s, 
                            'Buffer time before/after session for attendance marking')
                """
                self.cursor.execute(insert_query, (buffer_minutes,))
                self.mysql_connection.commit()
                
            print(f"📋 Session buffer time: {buffer_minutes} minutes")
            return buffer_minutes
        except mysql.connector.Error as err:
            print(f"⚠ Could not fetch buffer time, using default: {err}")
            return Config.SESSION_BUFFER_MINUTES

    def mark_attendance(self, User_ID, Name, Session_ID, Subject_ID):
        today = date.today()
        current_time = datetime.now()
        
        check_query = "SELECT * FROM Attendance WHERE User_ID = %s AND Session_ID = %s"
        self.cursor.execute(check_query, (User_ID, Session_ID))
        existing = self.cursor.fetchone()

        if existing:
            print(f"{Name} already marked present for this session")
            return False, f"{Name} already marked present"

        session_query = "SELECT Start_Time, Session_Date FROM Attendance_Session WHERE Session_ID = %s"
        self.cursor.execute(session_query, (Session_ID,))
        session = self.cursor.fetchone()

        if not session:
            print(f'Session {Session_ID} not found!!')
            return False, f"Session {Session_ID} not found"

        settings_query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'late_threshold_minutes'"
        self.cursor.execute(settings_query)
        setting = self.cursor.fetchone()
        late_threshold = int(setting['Setting_Value']) if setting else Config.LATE_THRESHOLD_MINUTES
        
        session_start = session['Start_Time']
        if isinstance(session_start, timedelta):
            total_seconds = int(session_start.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            session_start = time(hours, minutes, seconds)
        
        current_time_only = current_time.time()
        status = 'Present'

        session_start_dt = datetime.combine(today, session_start)
        current_dt = datetime.combine(today, current_time_only)
        time_diff = (current_dt - session_start_dt).total_seconds() / 60
        
        if time_diff > late_threshold:
            status = 'Late'
        
        insert_query = """INSERT INTO Attendance (Session_ID, User_ID, Subject_ID, Date, Check_In_Time, Status, Marked_By) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        try:
            self.cursor.execute(insert_query, (
                Session_ID, User_ID, Subject_ID, today,
                current_time, status, 'Face Recognition'
            ))
            self.mysql_connection.commit()

            print(f"✓ Attendance marked for {User_ID}: {Name} ({status})")
            return True, f"Attendance marked as {status}"

        except mysql.connector.Error as err:
            print(f"✗ Error marking attendance: {err}")
            self.mysql_connection.rollback()
            return False, f"Database error: {err}"

    # ... (rest of your file: create_attendance_session, get_active_session, recognize_user) ...
    # ... The 'recognize_user' function is for a live video feed, NOT for the API ...
    
    def get_active_session(self, Subject_ID=None, use_buffer=True):
        # ... (This function looks fine) ...
        today = date.today()
        # Note: You might want to check the *time* as well, not just the date
        
        if Subject_ID:
            query = """
                SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, Session_Type
                FROM Attendance_Session
                WHERE Subject_ID = %s 
                AND Session_Date = %s
                AND Status IN ('Scheduled', 'Ongoing')
                ORDER BY Start_Time ASC
            """
            self.cursor.execute(query, (Subject_ID, today))
        else:
            query = """
                SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, Session_Type
                FROM Attendance_Session
                WHERE Session_Date = %s
                AND Status IN ('Scheduled', 'Ongoing')
                ORDER BY Start_Time ASC
            """
            self.cursor.execute(query, (today,))
        
        sessions = self.cursor.fetchall()

        if sessions:
            print(f"✓ Found {len(sessions)} active session(s)")
        else:
            print("⚠ No active sessions found at this time")

        return sessions

    def close(self):
        self.cursor.close()
        self.mysql_connection.close()

# ... (Your __main__ block is fine for testing) ...