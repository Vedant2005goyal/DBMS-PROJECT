# api.py
# (I have added all the 'if not data' checks for robustness)

from flask import Flask, request, jsonify, send_from_directory 
from flask_cors import CORS
from database import DatabaseManager
import hashlib
from datetime import datetime, date, time, timedelta
import cv2
import numpy as np
import base64
import os
from config import Config

# --- IMPORT YOUR LOGIC FILES ---
from Mark_Attendance import MarkAttendance  # Import the class
from Face_Recognition import FaceRegistration # Import for face registration

# Get the project root directory (parent of backend)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER_PATH = os.path.join(PROJECT_ROOT, 'frontend')
app = Flask(__name__, static_folder=STATIC_FOLDER_PATH, static_url_path='')
CORS(app)  # Allow frontend to connect

# --- CREATE SINGLETON INSTANCES ---
# Create one instance of each class to be shared, just like your DB
# This is much more efficient than creating one on every request.
db = DatabaseManager()
marker = MarkAttendance()
registrar = FaceRegistration()


# Helper function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

# Yeh 'student-dashboard.html', 'mark_attendance.html', 'styles.css' etc. ko serve karega
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)



# ===== AUTHENTICATION =====
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        # Note: Passwords are stored as plain text in the database
        # If you want to use hashed passwords, update the database first
        query = """
            SELECT User_ID, Name, Email, User_Role 
            FROM User 
            WHERE Email = %s AND Password_Hash = %s
        """
        user = db.execute_query(query, (email, password), fetch_one=True)
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user['User_ID'],
                    'name': user['Name'],
                    'email': user['Email'],
                    'role': user['User_Role']
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    except Exception as e:
        print(f"Error in /api/login: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== ATTENDANCE =====
@app.route('/api/attendance/student/<int:user_id>', methods=['GET'])
def get_student_attendance(user_id):
    try:
        # Get attendance stats
        stats_query = """
            SELECT 
                COUNT(DISTINCT s.Session_ID) as total,
                COUNT(DISTINCT a.Attendance_ID) as present
            FROM Attendance_Session s
            LEFT JOIN Attendance a ON s.Session_ID = a.Session_ID 
                AND a.User_ID = %s
            WHERE s.Status = 'Completed'
        """
        stats = db.execute_query(stats_query, (user_id,), fetch_one=True)

        # FIXED: Check if stats is None
        if not stats:
            total = 0
            present = 0
        else:
            total = int(stats.get('total') or 0)
            present = int(stats.get('present') or 0)

        percentage = (present / total * 100) if total > 0 else 0
        
        # Get recent attendance
        attendance_query = """
            SELECT 
                a.Date, a.Status, a.Check_In_Time,
                sub.Subject_Name
            FROM Attendance a
            JOIN Subject sub ON a.Subject_ID = sub.Subject_ID
            WHERE a.User_ID = %s
            ORDER BY a.Date DESC
            LIMIT 20
        """
        attendance = db.execute_query(attendance_query, (user_id,), fetch=True) or []
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': total,
                'present_sessions': present,
                'absent_sessions': total - present,
                'percentage': round(percentage, 2)
            },
            'attendance': [{
                'date': str(record['Date']),
                'subject_name': record['Subject_Name'],
                'status': record['Status'],
                'time': str(record['Check_In_Time'])
            } for record in attendance]
        })
    
    except Exception as e:
        print(f"Error in /api/attendance/student: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== SESSION MANAGEMENT =====
@app.route('/api/session/create', methods=['POST'])
def create_session():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # TODO: Add validation for required fields
        
        query = """
            INSERT INTO Attendance_Session 
            (Subject_ID, Session_Date, Start_Time, End_Time, Session_Type, Status, Created_By)
            VALUES (%s, %s, %s, %s, %s, 'Scheduled', %s)
        """
        
        session_id = db.execute_query(query, (
            data['subject_id'],
            data['session_date'],
            data['start_time'],
            data['end_time'],
            data.get('session_type', 'Lecture'),
            data['created_by']
        ))
        
        return jsonify({
            'success': True,
            'session_id': session_id
        }), 201
    
    except Exception as e:
        print(f"Error in /api/session/create: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/<int:session_id>/status', methods=['PUT'])
def update_session_status(session_id):
    """Update session status (Scheduled, Ongoing, Completed)"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        new_status = data.get('status')
        if new_status not in ('Scheduled', 'Ongoing', 'Completed'):
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        query = "UPDATE Attendance_Session SET Status = %s WHERE Session_ID = %s"
        db.execute_query(query, (new_status, session_id))
        
        return jsonify({
            'success': True,
            'message': f'Session status updated to {new_status}'
        })
    except Exception as e:
        print(f"Error in /api/session/status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all active subjects"""
    try:
        query = """
            SELECT Subject_ID, Subject_Name, Subject_Code
            FROM Subject
            WHERE Is_Active = TRUE OR Is_Active IS NULL
            ORDER BY Subject_Name
        """
        subjects = db.execute_query(query, fetch=True) or []
        
        return jsonify({
            'success': True,
            'subjects': subjects
        })
    except Exception as e:
        print(f"Error in /api/subjects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/subjects', methods=['GET'])
def get_teacher_subjects():
    """Get subjects taught by a specific teacher"""
    try:
        teacher_id = request.args.get('teacher_id', type=int)
        if not teacher_id:
            return jsonify({'success': False, 'message': 'teacher_id required'}), 400
        
        # Try with Is_Active check first, if column doesn't exist, try without it
        try:
            query = """
                SELECT Subject_ID, Subject_Name, Subject_Code, Class_ID
                FROM Subject
                WHERE User_ID = %s AND (Is_Active = TRUE OR Is_Active IS NULL)
                ORDER BY Subject_Name
            """
            subjects = db.execute_query(query, (teacher_id,), fetch=True) or []
        except Exception as col_error:
            # If Is_Active column doesn't exist, query without it
            print(f"Is_Active column might not exist, trying without it: {col_error}")
            query = """
                SELECT Subject_ID, Subject_Name, Subject_Code, Class_ID
                FROM Subject
                WHERE User_ID = %s
                ORDER BY Subject_Name
            """
            subjects = db.execute_query(query, (teacher_id,), fetch=True) or []
        
        print(f"Found {len(subjects)} subjects for teacher_id {teacher_id}")
        
        return jsonify({
            'success': True,
            'subjects': subjects
        })
    except Exception as e:
        print(f"Error in /api/teacher/subjects: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/subject/<int:subject_id>', methods=['GET'])
def get_sessions_for_subject(subject_id):
    """Get all sessions for a specific subject"""
    try:
        query = """
            SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, 
                   Session_Type, Status, Created_By
            FROM Attendance_Session
            WHERE Subject_ID = %s
            ORDER BY Session_Date DESC, Start_Time DESC
        """
        sessions = db.execute_query(query, (subject_id,), fetch=True) or []
        
        # Convert time/date objects to strings
        for session in sessions:
            session['Session_Date'] = str(session['Session_Date'])
            session['Start_Time'] = str(session['Start_Time'])
            session['End_Time'] = str(session['End_Time'])
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        print(f"Error in /api/session/subject: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/attendance/session/<int:session_id>', methods=['GET'])
def get_session_attendance(session_id):
    """Get attendance for a specific session"""
    try:
        query = """
            SELECT 
                a.Attendance_ID,
                a.User_ID,
                u.Name as name,
                s.Roll_no,
                a.Status,
                a.Check_In_Time as time,
                a.Date
            FROM Attendance a
            JOIN User u ON a.User_ID = u.User_ID
            LEFT JOIN Students s ON a.User_ID = s.User_ID
            WHERE a.Session_ID = %s
            ORDER BY u.Name
        """
        attendance = db.execute_query(query, (session_id,), fetch=True) or []
        
        # Convert datetime to string
        for record in attendance:
            record['time'] = str(record['time']) if record['time'] else None
            record['Date'] = str(record['Date'])
        
        return jsonify({
            'success': True,
            'attendance': attendance
        })
    except Exception as e:
        print(f"Error in /api/attendance/session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/session/active', methods=['GET'])
def get_active_sessions():
    try:
        subject_id = request.args.get('subject_id', type=int)
        date_param = request.args.get('date')
        if date_param:
            today = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            today = date.today()
        
        query = """
            SELECT s.Session_ID, s.Subject_ID, s.Session_Date, s.Start_Time, s.End_Time, 
                   s.Session_Type, s.Status, s.Created_By, sub.Subject_Name
            FROM Attendance_Session s
            JOIN Subject sub ON s.Subject_ID = sub.Subject_ID
            WHERE s.Session_Date = %s
            AND s.Status IN ('Scheduled', 'Ongoing')
        """
        params: list[object] = [today]
        
        if subject_id:
            query += " AND s.Subject_ID = %s"
            params.append(subject_id)
        
        sessions = db.execute_query(query, tuple(params), fetch=True) or []
        
        # Convert time/date objects to strings for JSON
        for session in sessions:
            session['Session_Date'] = str(session['Session_Date'])
            session['Start_Time'] = str(session['Start_Time'])
            session['End_Time'] = str(session['End_Time'])

        return jsonify({
            'success': True,
            'sessions': sessions
        })
    
    except Exception as e:
        print(f"Error in /api/session/active: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def base64_to_image(base64_string):
    """Helper function to convert base64 string to an OpenCV image."""
    if "base64," in base64_string:
        header, data = base64_string.split('base64,', 1)
    else:
        data = base64_string
        
    try:
        img_data = base64.b64decode(data)
        img_np = np.frombuffer(img_data, dtype=np.uint8)
        image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"Could not decode base64 image: {e}")
        return None

# --- FACE ATTENDANCE ENDPOINT ---
@app.route('/api/mark-attendance', methods=['POST'])
def handle_mark_attendance():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        image_base64 = data.get('image')
        subject_id = data.get('subject_id')
        session_id = data.get('session_id')  # Optional: if provided, use it

        if not image_base64:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
        
        if not subject_id:
            return jsonify({'success': False, 'message': 'No subject_id provided'}), 400

        # 1. Convert Base64 string to an OpenCV image
        frame = base64_to_image(image_base64)
        
        if frame is None:
             return jsonify({'success': False, 'message': 'Could not decode image'}), 400

        # 2. Call the function from Mark_Attendance
        #    Pass session_id if provided
        if session_id:
            result = marker.mark_attendance_from_frame(frame, subject_id, session_id=session_id)
        else:
            result = marker.mark_attendance_from_frame(frame, subject_id) 
        
        # 3. Send the result back to the frontend
        if result['success']:
            return jsonify({
                'success': True, 
                'message': f"Attendance marked for {result['name']}",
                'name': result['name']
            })
        else:
            return jsonify({
                'success': False, 
                'message': result.get('message', 'Failed to mark attendance')
            })

    except Exception as e:
        print(f"Error in /api/mark-attendance: {e}")
        return jsonify({'success': False, 'message': 'An internal server error occurred'}), 500

# --- FACE REGISTRATION ENDPOINT ---
@app.route('/api/register-face', methods=['POST'])
def handle_register_face():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        user_id = data.get('user_id')
        image_base64 = data.get('image')

        if not user_id or not image_base64:
            return jsonify({'success': False, 'message': 'user_id and image are required'}), 400

        frame = base64_to_image(image_base64)
        if frame is None:
            return jsonify({'success': False, 'message': 'Could not decode image'}), 400
        
        # Call the registration logic
        # Note: This logic assumes the image is saved to a file first,
        # which FaceRegistration.py expects.
        # For a production system, you might modify FaceRegistration
        # to accept an image frame directly.
        
        # --- Simple temporary save ---
        temp_path = f"temp_register_{user_id}.jpg"
        cv2.imwrite(temp_path, frame)
        # -----------------------------
        
        result, message = registrar.register_person(user_id, temp_path,show_preview=True)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if result:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})

    except Exception as e:
        print(f"Error in /api/register-face: {e}")
        return jsonify({'success': False, 'message': 'An internal server error occurred'}), 500

@app.route('/api/subject/<int:subject_id>/students', methods=['GET'])
def get_subject_students(subject_id):
    """Get all students enrolled in a subject"""
    try:
        query = """
            SELECT DISTINCT 
                u.User_ID,
                u.Name,
                u.Email,
                s.Roll_no
            FROM User u
            JOIN Students s ON u.User_ID = s.User_ID
            JOIN Student_Subject ss ON u.User_ID = ss.User_ID
            WHERE ss.Subject_ID = %s
            ORDER BY s.Roll_no, u.Name
        """
        students = db.execute_query(query, (subject_id,), fetch=True) or []
        
        return jsonify({
            'success': True,
            'students': students
        })
    except Exception as e:
        print(f"Error in /api/subject/students: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/attendance/manual', methods=['POST'])
def mark_attendance_manual():
    """Mark attendance manually for a student"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        subject_id = data.get('subject_id')
        status = data.get('status', 'Present')  # Present, Late, or Absent
        
        if not user_id or not session_id or not subject_id:
            return jsonify({'success': False, 'message': 'user_id, session_id, and subject_id are required'}), 400
        
        # Check if already marked
        check_query = "SELECT * FROM Attendance WHERE User_ID = %s AND Session_ID = %s"
        existing = db.execute_query(check_query, (user_id, session_id), fetch_one=True)
        
        if existing:
            return jsonify({'success': False, 'message': 'Attendance already marked for this student'}), 400
        
        # Get session info for date
        session_query = "SELECT Session_Date, Start_Time FROM Attendance_Session WHERE Session_ID = %s"
        session = db.execute_query(session_query, (session_id,), fetch_one=True)
        
        if not session:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
        
        # Calculate if late (if status is Present, check time)
        check_in_time = datetime.now()
        session_date = session['Session_Date']
        session_start = session['Start_Time']
        
        # Convert session_start to time if needed
        if isinstance(session_start, timedelta):
            total_seconds = int(session_start.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            session_start = time(hours, minutes, seconds)
        
        # Check if late (only if status is Present)
        if status == 'Present':
            session_start_dt = datetime.combine(session_date, session_start)
            time_diff = (check_in_time - session_start_dt).total_seconds() / 60
            
            # Get late threshold
            settings_query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'late_threshold_minutes'"
            setting = db.execute_query(settings_query, fetch_one=True)
            late_threshold = int(setting['Setting_Value']) if setting else 10
            
            if time_diff > late_threshold:
                status = 'Late'
                print(f"Student marked as Late (arrived {time_diff:.1f} minutes after start)")
        
        # Insert attendance
        insert_query = """
            INSERT INTO Attendance (Session_ID, User_ID, Subject_ID, Date, Check_In_Time, Status, Marked_By)
            VALUES (%s, %s, %s, %s, %s, %s, 'Manual')
        """
        db.execute_query(insert_query, (
            session_id, user_id, subject_id, session_date,
            check_in_time, status
        ))
        
        # Get student name for response
        user_query = "SELECT Name FROM User WHERE User_ID = %s"
        student = db.execute_query(user_query, (user_id,), fetch_one=True)
        student_name = student['Name'] if student else 'Student'
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked as {status} for {student_name}',
            'status': status
        })
    except Exception as e:
        print(f"Error in /api/attendance/manual: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Run server
if __name__ == '__main__':
    # Make sure to load config
    try:
        c=Config()
        c.validate()
        print("Configuration validated.")
    except ValueError as e:
        print(f"!!! CONFIGURATION ERROR: {e} !!!")
        print("Please check your .env file")
        exit(1) # Uncomment this to force exit on bad config
    
    app.run(host='0.0.0.0', port=5000, debug=True)