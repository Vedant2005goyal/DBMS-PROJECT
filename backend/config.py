import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'attendance_system')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    
    # Face Recognition Settings
    FACE_RECOGNITION_TOLERANCE = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.55))
    PHOTO_STORAGE_PATH = os.getenv('PHOTO_STORAGE_PATH', './student_photos')
    
    # Application Settings
    MIN_ATTENDANCE_PERCENTAGE = int(os.getenv('MIN_ATTENDANCE_PERCENTAGE', 75))
    LATE_THRESHOLD_MINUTES = int(os.getenv('LATE_THRESHOLD_MINUTES', 10))
    SESSION_BUFFER_MINUTES = int(os.getenv('SESSION_BUFFER_MINUTES', 5))
    
    # Automation Settings
    AUTO_NOTIFY_ENABLED = os.getenv('AUTO_NOTIFY_ENABLED', 'False').lower() == 'true'
    AUTO_NOTIFY_SCHEDULE = os.getenv('AUTO_NOTIFY_SCHEDULE', '18:00')  # Daily at 6 PM
    
    # Cloud Storage (Optional - for AWS S3, Google Cloud Storage)
    CLOUD_STORAGE_ENABLED = os.getenv('CLOUD_STORAGE_ENABLED', 'False').lower() == 'true'
    CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET', '')
    CLOUD_STORAGE_REGION = os.getenv('CLOUD_STORAGE_REGION', 'us-east-1')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    @classmethod
    def validate(cls):
        """Validate essential configurations"""
        required = [
            ('DB_PASSWORD', cls.DB_PASSWORD),
            ('SENDER_EMAIL', cls.SENDER_EMAIL),
            ('SENDER_PASSWORD', cls.SENDER_PASSWORD),
        ]
        
        missing = [key for key, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        return True
