# Attendance Management System

A modern, containerized attendance management system with face recognition capabilities, built with Flask, MySQL, and Docker.

## Features

- 🎯 **Face Recognition Attendance**: Mark attendance using facial recognition
- 📊 **Student Dashboard**: View attendance statistics and history
- 📧 **Automated Notifications**: Email notifications for low attendance
- 🔐 **Secure Authentication**: User login with role-based access
- 🐳 **Dockerized**: Easy deployment with Docker Compose
- 📱 **Responsive UI**: Beautiful, modern frontend design

## Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- At least 4GB of RAM available for Docker

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd dbms_project
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=your_secure_password_here
DB_NAME=attendance_system
DB_PORT=3306

# Email Configuration (for notifications)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE=0.55
PHOTO_STORAGE_PATH=./student_photos

# Application Settings
MIN_ATTENDANCE_PERCENTAGE=75
LATE_THRESHOLD_MINUTES=10
SESSION_BUFFER_MINUTES=5

# Automation Settings
AUTO_NOTIFY_ENABLED=true
AUTO_NOTIFY_SCHEDULE=18:00

# Security
SECRET_KEY=your-secret-key-change-in-production
```

**Note**: For Gmail, you'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### 3. Deploy the Application

Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
# Build and start containers
docker-compose up -d --build

# Wait for database to initialize
sleep 15

# Initialize database schema (if not already done)
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < schema.sql
```

### 4. Access the Application

- **Frontend**: http://localhost:5001
- **API**: http://localhost:5001/api

**Note**: Port 5001 is used because port 5000 is typically occupied by macOS AirPlay Receiver.

## Project Structure

```
dbms_project/
├── backend/              # Flask API backend
│   ├── api.py           # Main Flask application
│   ├── database.py      # Database connection manager
│   ├── config.py        # Configuration management
│   ├── Face_Recognition.py
│   ├── Mark_Attendance.py
│   ├── Notification.py
│   └── scheduler.py
├── frontend/            # Frontend HTML/CSS/JS
│   ├── index.html       # Login page
│   ├── student_dashboard.html
│   ├── mark_attendance.html
│   └── styles.css
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Backend container definition
├── schema.sql          # Database schema
├── deploy.sh           # Deployment script
└── requirements.txt    # Python dependencies
```

## Services

The application consists of three Docker services:

1. **MySQL Database** (`mysql`)
   - Port: 3306
   - Persistent data storage
   - Auto-initializes with schema.sql

2. **API Server** (`api`)
   - Port: 5001 (host) → 5000 (container)
   - Flask REST API
   - Serves frontend static files

3. **Scheduler** (`scheduler`)
   - Background service for automated notifications
   - Runs scheduled attendance checks

## Usage

### Login

Default test credentials (from sample data):
- Email: `vgoyal@thapar.edu`
- Password: `uf422ets@`

**Note**: Passwords in the database should be stored as SHA256 hashes. Update your database accordingly.

### Mark Attendance

1. Login as a student
2. Navigate to "Mark Attendance"
3. Select a subject from the dropdown
4. Allow camera access when prompted
5. Click "Mark My Attendance"
6. Your face will be recognized and attendance will be recorded

### View Attendance

- Students can view their attendance statistics and history on the dashboard
- **Overall attendance percentage** across all subjects
- **Per-subject attendance breakdown** with individual percentages
- Classes attended and missed counts
- Recent attendance records are shown in a table with color-coded status

## Development

### Running Locally (Without Docker)

1. Install Python 3.9+ and MySQL
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up MySQL database and update `.env` with `DB_HOST=localhost`
5. Run the application:
   ```bash
   cd backend
   python api.py
   ```

### Database Management

Access MySQL container:
```bash
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME}
```

View logs:
```bash
docker-compose logs -f api
docker-compose logs -f scheduler
docker-compose logs -f mysql
```

### Stopping the Application

```bash
docker-compose down
```

To remove volumes (deletes database data):
```bash
docker-compose down -v
```

## Troubleshooting

### Database Connection Issues

- Ensure MySQL container is running: `docker-compose ps`
- Check database credentials in `.env`
- Wait a few seconds after starting containers for MySQL to initialize

### Face Recognition Not Working

- Ensure student faces are registered in the database
- Check camera permissions in browser
- Verify `student_photos` directory exists and has proper permissions

### Port Already in Use

If port 5001 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "5002:5000"  # Change 5002 to any available port
```
Then update `API_URL` in all frontend HTML files to match the new port.

### Email Notifications Not Sending

- Verify email credentials in `.env`
- For Gmail, use App Password, not regular password
- Check SMTP settings match your email provider

## Production Deployment

For production deployment:

1. Change `SECRET_KEY` in `.env` to a strong random value
2. Use strong database passwords
3. Set up SSL/TLS for HTTPS
4. Configure proper firewall rules
5. Set up regular database backups
6. Use environment-specific configurations
7. Enable proper logging and monitoring

## API Endpoints

- `POST /api/login` - User authentication
- `GET /api/attendance/student/<user_id>` - Get student attendance
- `GET /api/subjects` - Get all subjects
- `GET /api/session/active` - Get active sessions
- `POST /api/mark-attendance` - Mark attendance via face recognition
- `POST /api/register-face` - Register student face
- `POST /api/session/create` - Create attendance session

## Technologies Used

- **Backend**: Python, Flask, MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Face Recognition**: face_recognition library, OpenCV
- **Database**: MySQL 8.0
- **Containerization**: Docker, Docker Compose
- **Email**: SMTP

## License

This project is for educational purposes.

## Support

For issues or questions, please check the logs:
```bash
docker-compose logs -f
```

