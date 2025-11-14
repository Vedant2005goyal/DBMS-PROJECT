#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import json


# In[4]:


class NotificationSystem:
    def __init__(self):
        try:
            self.mysql_connection=mysql.connector.connect(
                host="localhost",
                user="root",
                password="goyalvedant2005",
                database="attendance_system"
            )
            self.cursor = self.mysql_connection.cursor(dictionary=True)
            print('Database connected succesfully!!')
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            raise
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 465
        self.sender_email = "goyalvedant2005@gmail.com"  
        self.sender_password = "inig vfvg qwdg zvyi" 

    def get_min_attendance_percentage(self):
        try:
            query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'min_attendance_percentage'"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return int(result['Setting_Value']) if result else 75
        except:
            return 75

    def calculate_student_attendance(self, user_id, subject_id=None):
        if subject_id:
            query = """SELECT COUNT(DISTINCT s.Session_ID) as total FROM Attendance_Session s
                    WHERE s.Subject_ID = %s AND s.Status = 'Completed' """
            self.cursor.execute(query, (subject_id,))
            total_sessions = self.cursor.fetchone()['total']

            present_query = """SELECT COUNT(*) as present FROM Attendance a WHERE a.User_ID = %s 
                AND a.Subject_ID = %s AND a.Status IN ('Present', 'Late') """
            self.cursor.execute(present_query, (user_id, subject_id))
            present_sessions = self.cursor.fetchone()['present']
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
            total_sessions = self.cursor.fetchone()['total']

            present_query = """
                SELECT COUNT(*) as present
                FROM Attendance a
                WHERE a.User_ID = %s
                AND a.Status IN ('Present', 'Late')
            """
            self.cursor.execute(present_query, (user_id,))
            present_sessions = self.cursor.fetchone()['present']

        if total_sessions == 0:
            percentage = 0
        else:
            percentage = (present_sessions / total_sessions) * 100

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

        for student in students:
            attendance = self.calculate_student_attendance(student['User_ID'], subject_id)

            if attendance['percentage'] < min_percentage:
                low_attendance_students.append({
                    'user_id': student['User_ID'],
                    'name': student['Name'],
                    'email': student['Email'],
                    'roll_no': student['Roll_no'],
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

            # Connect and send
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
        min_percentage = self.get_min_attendance_percentage()

        subject_text = f" in {subject_name}" if subject_name else ""

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px;">
                <h2 style="color: #d9534f;">⚠️ Low Attendance Alert</h2>

                <p>Dear <strong>{student_name}</strong>,</p>

                <p>This is to inform you that your attendance{subject_text} is below the required minimum.</p>

                <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #721c24;">Attendance Summary:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li> <strong>Current Attendance:</strong> {attendance_data['percentage']}%</li>
                        <li> <strong>Present:</strong> {attendance_data['present_sessions']} sessions</li>
                        <li> <strong>Absent:</strong> {attendance_data['absent_sessions']} sessions</li>
                        <li> <strong>Total Sessions:</strong> {attendance_data['total_sessions']}</li>
                        <li> <strong>Required Minimum:</strong> {min_percentage}%</li>
                    </ul>
                </div>

                <p style="color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;">
                    <strong>Action Required:</strong> Please ensure you attend all upcoming classes to improve your attendance.
                </p>

                <p>If you have any concerns, please contact your class coordinator.</p>

                <hr style="margin: 20px 0;">

                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the Attendance Management System.<br>
                    Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def create_parent_email_body(self, student_name, attendance_data, subject_name=None):
        """Create HTML email body for parent"""
        min_percentage = self.get_min_attendance_percentage()

        subject_text = f" in {subject_name}" if subject_name else ""

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px;">
                <h2 style="color: #d9534f;">⚠️ Student Attendance Alert</h2>

                <p>Dear Parent/Guardian,</p>

                <p>This is to inform you that your ward <strong>{student_name}</strong> has low attendance{subject_text}.</p>

                <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #721c24;">Attendance Details:</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li> <strong>Student:</strong> {student_name}</li>
                        <li> <strong>Attendance Percentage:</strong> {attendance_data['percentage']}%</li>
                        <li> <strong>Classes Attended:</strong> {attendance_data['present_sessions']}</li>
                        <li> <strong>Classes Missed:</strong> {attendance_data['absent_sessions']}</li>
                        <li> <strong>Total Classes:</strong> {attendance_data['total_sessions']}</li>
                        <li> <strong>Required Minimum:</strong> {min_percentage}%</li>
                    </ul>
                </div>

                <p style="color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;">
                    <strong>Immediate Attention Required:</strong> Please ensure your ward attends all classes regularly.
                </p>

                <p>For any queries or concerns, please contact the class coordinator or visit the institution.</p>

                <hr style="margin: 20px 0;">

                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from the Attendance Management System.<br>
                    Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def create_teacher_summary_email(self, low_attendance_list, subject_name=None):
        """Create summary email for teacher"""
        subject_text = f" for {subject_name}" if subject_name else ""

        # Create table rows for each student
        student_rows = ""
        for student in low_attendance_list:
            status_color = "#d44e4a" if student['attendance']['percentage'] < 50 else "#f0ad4e"
            student_rows += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{student['name']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{student['roll_no']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; color: {status_color}; font-weight: bold;">
                    {student['attendance']['percentage']}%
                </td>
                <td style="padding: 10px; border: 1px solid #ddd;">{student['attendance']['present_sessions']}/{student['attendance']['total_sessions']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{student['attendance']['absent_sessions']}</td>
            </tr>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; border: 1px solid #ddd; border-radius: 10px; padding: 20px;">
                <h2 style="color: #5bc0de;"> Low Attendance Report{subject_text}</h2>

                <p>Dear Faculty,</p>

                <p>Below is the list of students with attendance below the minimum threshold:</p>

                <div style="margin: 20px 0; overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Student Name</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Roll No</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Attendance %</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Present/Total</th>
                                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Absent</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_rows}
                        </tbody>
                    </table>
                </div>

                <p><strong>Total Students with Low Attendance:</strong> {len(low_attendance_list)}</p>

                <p style="color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;">
                    <strong>Note:</strong> You can send notifications to parents using the notification system.
                </p>

                <hr style="margin: 20px 0;">

                <p style="color: #666; font-size: 12px;">
                    Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def notify_student(self, user_id, subject_id=None):
        """Send notification to a specific student"""
        # Get student details
        query = "SELECT u.Name, u.Email FROM User u WHERE u.User_ID = %s"
        self.cursor.execute(query, (user_id,))
        student = self.cursor.fetchone()

        if not student:
            print(f"✗ Student with ID {user_id} not found")
            return False

        # Get subject name if provided
        subject_name = None
        if subject_id:
            sub_query = "SELECT Subject_Name FROM Subject WHERE Subject_ID = %s"
            self.cursor.execute(sub_query, (subject_id,))
            subject_result = self.cursor.fetchone()
            subject_name = subject_result['Subject_Name'] if subject_result else None

        # Calculate attendance
        attendance = self.calculate_student_attendance(user_id, subject_id)

        # Create and send email
        subject_text = f" - {subject_name}" if subject_name else ""
        email_subject = f" Low Attendance Alert{subject_text}"
        email_body = self.create_student_email_body(student['Name'], attendance, subject_name)

        return self.send_email(student['Email'], email_subject, email_body)

    def notify_parent(self, user_id, subject_id=None):
        """Send notification to parent of a specific student"""
        # Get student and parent details
        query = """
            SELECT u.Name, s.Parent_Email 
            FROM User u
            JOIN Students s ON u.User_ID = s.User_ID
            WHERE u.User_ID = %s
        """
        self.cursor.execute(query, (user_id,))
        student = self.cursor.fetchone()

        if not student or not student['Parent_Email']:
            print(f"✗ Parent email not found for student ID {user_id}")
            return False

        # Get subject name if provided
        subject_name = None
        if subject_id:
            sub_query = "SELECT Subject_Name FROM Subject WHERE Subject_ID = %s"
            self.cursor.execute(sub_query, (subject_id,))
            subject_result = self.cursor.fetchone()
            subject_name = subject_result['Subject_Name'] if subject_result else None

        # Calculate attendance
        attendance = self.calculate_student_attendance(user_id, subject_id)

        # Create and send email
        subject_text = f" - {subject_name}" if subject_name else ""
        email_subject = f"Your Ward's Attendance Alert{subject_text}"
        email_body = self.create_parent_email_body(student['Name'], attendance, subject_name)

        return self.send_email(student['Parent_Email'], email_subject, email_body)

    def notify_teacher(self, faculty_id, subject_id=None):
        """Send summary report to teacher"""
        # Get teacher email
        query = "SELECT u.Email, u.Name FROM User u WHERE u.User_ID = %s"
        self.cursor.execute(query, (faculty_id,))
        teacher = self.cursor.fetchone()

        if not teacher:
            print(f"✗ Faculty with ID {faculty_id} not found")
            return False

        # Get subject name if provided
        subject_name = None
        if subject_id:
            sub_query = "SELECT Subject_Name FROM Subject WHERE Subject_ID = %s"
            self.cursor.execute(sub_query, (subject_id,))
            subject_result = self.cursor.fetchone()
            subject_name = subject_result['Subject_Name'] if subject_result else None

        # Get low attendance students
        low_attendance_students = self.get_low_attendance_students(subject_id)

        if not low_attendance_students:
            print(f"✓ No students with low attendance")
            return False

        # Create and send email
        subject_text = f" - {subject_name}" if subject_name else ""
        email_subject = f"Low Attendance Report{subject_text}"
        email_body = self.create_teacher_summary_email(low_attendance_students, subject_name)

        return self.send_email(teacher['Email'], email_subject, email_body)

    def bulk_notify_low_attendance(self, subject_id=None, notify_parents=False):
        """
        Send notifications to all students with low attendance

        Args:
            subject_id: Filter by subject (optional)
            notify_parents: Also send to parents (default: False)

        Returns:
            Statistics of notifications sent
        """
        low_attendance_students = self.get_low_attendance_students(subject_id)

        stats = {
            'total_students': len(low_attendance_students),
            'students_notified': 0,
            'parents_notified': 0,
            'failed': 0
        }

        print(f"\n{'='*60}")
        print(f"SENDING NOTIFICATIONS TO {stats['total_students']} STUDENTS")
        print(f"{'='*60}\n")

        for student in low_attendance_students:
            print(f"Processing: {student['name']} ({student['roll_no']})")

            # Notify student
            if self.notify_student(student['user_id'], subject_id):
                stats['students_notified'] += 1
            else:
                stats['failed'] += 1

            # Notify parent if requested
            if notify_parents:
                if self.notify_parent(student['user_id'], subject_id):
                    stats['parents_notified'] += 1

        print(f"\n{'='*60}")
        print(f"NOTIFICATION SUMMARY")
        print(f"{'='*60}")
        print(f"✓ Students notified: {stats['students_notified']}")
        print(f"✓ Parents notified: {stats['parents_notified']}")
        print(f"✗ Failed: {stats['failed']}")
        print(f"{'='*60}\n")

        return stats

    def interactive_parent_notification(self, subject_id=None):
        """Interactive mode for teacher to select students for parent notification"""
        low_attendance_students = self.get_low_attendance_students(subject_id)

        if not low_attendance_students:
            print("✓ No students with low attendance found!")
            return

        print(f"\n{'='*70}")
        print("STUDENTS WITH LOW ATTENDANCE")
        print(f"{'='*70}")
        print(f"{'No.':<5} {'Name':<25} {'Roll No':<12} {'Attendance':<12}")
        print(f"{'-'*70}")

        for i, student in enumerate(low_attendance_students, 1):
            print(f"{i:<5} {student['name']:<25} {student['roll_no']:<12} {student['attendance']['percentage']}%")

        print(f"{'-'*70}")
        print("\nOptions:")
        print("  - Enter student numbers separated by commas (e.g., 1,3,5)")
        print("  - Enter 'all' to notify all parents")
        print("  - Enter 'exit' to cancel")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'exit':
            print("✗ Cancelled")
            return

        selected_students = []

        if choice == 'all':
            selected_students = low_attendance_students
        else:
            try:
                indices = [int(x.strip()) for x in choice.split(',')]
                selected_students = [low_attendance_students[i-1] for i in indices if 1 <= i <= len(low_attendance_students)]
            except:
                print("✗ Invalid input")
                return

        # Confirm
        print(f"\n You are about to send emails to {len(selected_students)} parent(s)")
        confirm = input("Continue? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("✗ Cancelled")
            return

        # Send notifications
        print(f"\n{'='*60}")
        print("SENDING PARENT NOTIFICATIONS")
        print(f"{'='*60}\n")

        success = 0
        failed = 0

        for student in selected_students:
            print(f"Notifying parent of {student['name']}...")
            if self.notify_parent(student['user_id'], subject_id):
                success += 1
            else:
                failed += 1

        print(f"\n✓ Successfully sent: {success}")
        print(f"✗ Failed: {failed}")

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.mysql_connection.close()
        print("✓ Connection closed")



# In[5]:


if __name__ == "__main__":
    notification = NotificationSystem()

    # Example 1: Notify a specific student
    print("\n--- Example 1: Notify Single Student ---")
    # notification.notify_student(user_id=21, subject_id=1009)

    # Example 2: Notify parent of a specific student
    print("\n--- Example 2: Notify Parent ---")
    # notification.notify_parent(user_id=21, subject_id=1009)

    # Example 3: Send teacher summary
    print("\n--- Example 3: Teacher Summary ---")
    # notification.notify_teacher(faculty_id=3, subject_id=1009)

    # Example 4: Bulk notify all low attendance students
    print("\n--- Example 4: Bulk Notification ---")
    # notification.bulk_notify_low_attendance(subject_id=1009, notify_parents=False)

    # Example 5: Interactive mode for teacher
    print("\n--- Example 5: Interactive Parent Notification ---")
    notification.interactive_parent_notification(subject_id=1009)

    notification.close()


# In[ ]:




