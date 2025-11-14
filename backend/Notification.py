#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import json
from config import Config  # <-- IMPORT CONFIG

class NotificationSystem:
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
            print('NotificationSystem: Database connected successfully!!')
        except mysql.connector.Error as err:
            print(f"NotificationSystem: Database connection failed: {err}")
            raise
        
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.sender_email = Config.SENDER_EMAIL
        self.sender_password = Config.SENDER_PASSWORD

    def get_min_attendance_percentage(self):
        try:
            query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'min_attendance_percentage'"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            # FIXED: Use .get() for safety.
            if result and result.get('Setting_Value') is not None:
                return int(result.get('Setting_Value'))
            return Config.MIN_ATTENDANCE_PERCENTAGE # Default fallback
        except:
            return Config.MIN_ATTENDANCE_PERCENTAGE

    def calculate_student_attendance(self, user_id, subject_id=None):
        total_sessions = 0
        present_sessions = 0

        if subject_id:
            query = """SELECT COUNT(DISTINCT s.Session_ID) as total FROM Attendance_Session s
                    WHERE s.Subject_ID = %s AND s.Status = 'Completed' """
            self.cursor.execute(query, (subject_id,))
            total_result = self.cursor.fetchone()

            # FIXED: Safely check for None and use .get()
            if total_result and total_result.get('total') is not None:
                total_sessions = int(total_result.get('total'))
            else:
                total_sessions = 0

            present_query = """SELECT COUNT(*) as present FROM Attendance a WHERE a.User_ID = %s 
                AND a.Subject_ID = %s AND a.Status IN ('Present', 'Late') """
            self.cursor.execute(present_query, (user_id, subject_id))
            present_result = self.cursor.fetchone()
            
            # FIXED: Safely check for None and use .get()
            if present_result and present_result.get('present') is not None:
                present_sessions = int(present_result.get('present'))
            else:
                present_sessions = 0
        else:
            # Overall attendance across all subjects
            total_query = """
                SELECT COUNT(DISTINCT s.Session_ID) as total
                FROM Attendance_Session s
                JOIN Student_Subject ss ON s.Subject_ID = ss.Subject_ID
                WHERE ss.User_ID = %s 
                AND s.Status = 'Completed'
            """
            self.cursor.execute(total_query, (user_id,))
            total_result = self.cursor.fetchone()

            # FIXED: Safely check for None and use .get()
            if total_result and total_result.get('total') is not None:
                total_sessions = int(total_result.get('total'))
            else:
                total_sessions = 0

            present_query = """
                SELECT COUNT(*) as present
                FROM Attendance a
                WHERE a.User_ID = %s
                AND a.Status IN ('Present', 'Late')
            """
            self.cursor.execute(present_query, (user_id,))
            present_result = self.cursor.fetchone()

            # FIXED: Safely check for None and use .get()
            if present_result and present_result.get('present') is not None:
                present_sessions = int(present_result.get('present'))
            else:
                present_sessions = 0

        if total_sessions == 0:
            percentage = 0.0
        else:
            # These are now guaranteed to be numbers
            percentage = (float(present_sessions) / float(total_sessions)) * 100

        return {
            'total_sessions': total_sessions,
            'present_sessions': present_sessions,
            'absent_sessions': total_sessions - present_sessions,
            'percentage': round(percentage, 2)
        }


    def get_low_attendance_students(self, subject_id=None):
        min_percentage = self.get_min_attendance_percentage()
        low_attendance_students = []

        # Get all students (optionally filtered by subject)
        if subject_id:
            query = """SELECT DISTINCT u.User_ID, u.Name, u.Email, s.Roll_no FROM User u
                    JOIN Students s ON u.User_ID = s.User_ID JOIN Student_Subject ss ON u.User_ID = ss.User_ID
                WHERE ss.Subject_ID = %s
            """
            self.cursor.execute(query, (subject_id,))
        else:
            query = """
                SELECT u.User_ID, u.Name, u.Email, s.Roll_no
                FROM User u
                JOIN Students s ON u.User_ID = s.User_ID
            """
            self.cursor.execute(query)

        students = self.cursor.fetchall()

        # FIXED: Check if students is None before iterating
        if not students:
            return []

        for student in students:
            # FIXED: Safely get user_id
            user_id = student.get('User_ID')
            if not user_id:
                continue # Skip student if they have no ID

            attendance = self.calculate_student_attendance(user_id, subject_id)

            if attendance['percentage'] < min_percentage:
                # FIXED: Use .get() for all student fields
                low_attendance_students.append({
                    'user_id': user_id,
                    'name': student.get('Name', 'Unknown'),
                    'email': student.get('Email'),
                    'roll_no': student.get('Roll_no', 'N/A'),
                    'attendance': attendance
                })

        return low_attendance_students

    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
        
            print(f"✓ Email sent to {to_email}")
            return True
        
        except Exception as e:
            print(f"✗ Failed to send email to {to_email}: {e}")
            return False
        
    def create_student_email_body(self, student_name, attendance_data, subject_name=None):
        """Create HTML email body for student"""
        min_percentage = self.get_min_attendance_percentage()
        
        subject_text = f" in {subject_name}" if subject_name else ""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>⚠️ Low Attendance Alert</h2>
            <p>Dear {student_name},</p>
            <p>Your attendance{subject_text} is {attendance_data['percentage']}%</p>
            <p>Required minimum: {min_percentage}%</p>
        </body>
        </html>
        """
        return html

def notify_student(self, user_id, subject_id=None):
    """Send notification to student"""
    query = "SELECT u.Name, u.Email FROM User u WHERE u.User_ID = %s"
    self.cursor.execute(query, (user_id,))
    student = self.cursor.fetchone()
    
    if not student:
        return False
    
    attendance = self.calculate_student_attendance(user_id, subject_id)
    email_body = self.create_student_email_body(student['Name'], attendance)
    
    return self.send_email(student['Email'], "Low Attendance Alert", email_body)

def close(self):
    self.cursor.close()
    self.mysql_connection.close()