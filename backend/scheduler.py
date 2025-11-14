import schedule
import time
from datetime import datetime
from Notification import NotificationSystem
from config import Config
import logging
from database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance_automation.log'),
        logging.StreamHandler()
    ]
)

class AttendanceScheduler:
    def __init__(self):
        self.db = DatabaseManager()
        self.notification_system = NotificationSystem()
        logging.info("Scheduler initialized")
    
    def auto_close_sessions(self):
        """Mark sessions as Completed once their end time has passed."""
        try:
            query = """
                UPDATE Attendance_Session
                SET Status = 'Completed'
                WHERE Status IN ('Scheduled', 'Ongoing')
                  AND TIMESTAMP(Session_Date, End_Time) < NOW()
            """
            self.db.execute_query(query)
            logging.info("Auto-close check executed")
        except Exception as e:
            logging.error(f"Failed to auto-close sessions: {e}")
    
    def daily_attendance_check(self):
        """Run daily attendance check and send notifications"""
        logging.info("=== Starting Daily Attendance Check ===")
        
        try:
            # Get all subjects
            subjects = self.get_all_subjects()
            
            total_notifications = 0
            
            for subject in subjects:
                subject_id = subject['Subject_ID']
                subject_name = subject['Subject_Name']
                
                logging.info(f"Checking attendance for: {subject_name} (ID: {subject_id})")
                
                # Get low attendance students
                low_attendance = self.notification_system.get_low_attendance_students(subject_id)
                
                if low_attendance:
                    logging.info(f"Found {len(low_attendance)} students with low attendance")
                    
                    # Notify students
                    for student in low_attendance:
                        try:
                            self.notification_system.notify_student(
                                student['user_id'],
                                subject_id
                            )
                            total_notifications += 1
                        except Exception as e:
                            logging.error(f"Failed to notify student {student['name']}: {e}")
                    
                    # Notify teacher
                    faculty_id = subject.get('User_ID')
                    if faculty_id:
                        try:
                            self.notification_system.notify_teacher(faculty_id, subject_id)
                        except Exception as e:
                            logging.error(f"Failed to notify teacher for subject {subject_name}: {e}")
            
            logging.info(f"=== Daily Check Complete. Sent {total_notifications} notifications ===")
            
        except Exception as e:
            logging.error(f"Error in daily attendance check: {e}")
    
    def get_all_subjects(self):
        """Get all active subjects"""
        db = DatabaseManager()
        query = "SELECT Subject_ID, Subject_Name, User_ID FROM Subject WHERE Is_Active = TRUE"
        try:
            result = db.execute_query(query, fetch=True)
            # Ensure we always return an iterable (empty list if no results)
            if not result:
                logging.info("No active subjects found in database")
                return []
            return result
        except Exception as e:
            logging.error(f"Failed to fetch subjects: {e}")
            return []
    
    def weekly_summary(self):
        """Generate and send weekly summary reports"""
        logging.info("=== Generating Weekly Summary ===")
        
        try:
            subjects = self.get_all_subjects()
            
            if not subjects:
                logging.warning("No subjects found for weekly summary")
                return
            
            for subject in subjects:
                faculty_id = subject.get('User_ID')
                if faculty_id:
                    self.notification_system.notify_teacher(faculty_id, subject['Subject_ID'])
            
            logging.info("=== Weekly Summary Complete ===")
        except Exception as e:
            logging.error(f"Error in weekly summary: {e}")
    
    def start(self):
        """Start the scheduler"""
        logging.info("Starting Attendance Automation Scheduler")
        
        # Auto close sessions every minute
        schedule.every(1).minutes.do(self.auto_close_sessions)
        logging.info("Scheduled auto-close job to run every minute")
        
        if Config.AUTO_NOTIFY_ENABLED:
            # Daily notification at specified time
            schedule.every().day.at(Config.AUTO_NOTIFY_SCHEDULE).do(self.daily_attendance_check)
            logging.info(f"Scheduled daily check at {Config.AUTO_NOTIFY_SCHEDULE}")
            
            # Weekly summary every Monday at 9 AM
            schedule.every().monday.at("09:00").do(self.weekly_summary)
            logging.info("Scheduled weekly summary on Mondays at 09:00")
        else:
            logging.warning("Automation is disabled in config")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
