from flask import Flask, request, jsonify
from flask_cors import CORS
from Face_Recognition import FaceRegistration
from Mark_Attendance import MarkAttendance
from Notification import NotificationSystem
from config import Config
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# Initialize systems
face_reg = FaceRegistration()
attendance = MarkAttendance()
notification = NotificationSystem()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/register-face', methods=['POST'])
def register_face():
    """Register a student's face"""
    try:
        data = request.json
        user_id = data.get('user_id')
        image_path = data.get('image_path')
        
        success = face_reg.register_face(user_id, image_path)
        
        return jsonify({
            'success': success,
            'message': 'Face registered successfully' if success else 'Registration failed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-session', methods=['POST'])
def create_session():
    """Create attendance session"""
    try:
        data = request.json
        session_id = attendance.create_attendance_session(
            Subject_ID=data['subject_id'],
            Session_Date=data['session_date'],
            Start_Time=data['start_time'],
            End_Time=data['end_time'],
            Session_Type=data.get('session_type', 'Lecture'),
            Status='Scheduled',
            Created_By=data['created_by']
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/attendance/low', methods=['GET'])
def get_low_attendance():
    """Get students with low attendance"""
    try:
        subject_id = request.args.get('subject_id', type=int)
        students = notification.get_low_attendance_students(subject_id)
        
        return jsonify({
            'success': True,
            'count': len(students),
            'students': students
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notify/student', methods=['POST'])
def notify_student():
    """Send notification to student"""
    try:
        data = request.json
        success = notification.notify_student(
            data['user_id'],
            data.get('subject_id')
        )
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notify/parent', methods=['POST'])
def notify_parent():
    """Send notification to parent"""
    try:
        data = request.json
        success = notification.notify_parent(
            data['user_id'],
            data.get('subject_id')
        )
        
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notify/bulk', methods=['POST'])
def notify_bulk():
    """Send bulk notifications"""
    try:
        data = request.json
        stats = notification.bulk_notify_low_attendance(
            subject_id=data.get('subject_id'),
            notify_parents=data.get('notify_parents', False)
        )
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    Config.validate()
    app.run(host='0.0.0.0', port=5000, debug=False)

