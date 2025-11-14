#!/bin/bash

# Script to import subjects into the database
# This ensures teachers have subjects assigned

echo "🔧 Fixing Teacher-Subject Assignments"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please create a .env file with DB_PASSWORD"
    exit 1
fi

# Source .env to get DB_PASSWORD
source .env

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD not found in .env file"
    exit 1
fi

echo "✅ Found database password"
echo ""

# Check if Docker containers are running
if ! docker ps | grep -q attendance_db; then
    echo "❌ Database container is not running!"
    echo "   Start it with: docker-compose up -d"
    exit 1
fi

echo "✅ Database container is running"
echo ""

echo "📥 Importing subjects and fixing assignments..."
echo ""

# Import the SQL file
docker exec -i attendance_db mysql -u root -p"${DB_PASSWORD}" attendance_system < fix_teacher_subjects_complete.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Subjects imported successfully!"
    echo ""
    echo "📊 Verifying assignments..."
    docker exec attendance_db mysql -u root -p"${DB_PASSWORD}" attendance_system -e "
        SELECT 
            f.User_ID,
            u.Name as Teacher_Name,
            COUNT(s.Subject_ID) as Subject_Count
        FROM Faculty f
        LEFT JOIN User u ON f.User_ID = u.User_ID
        LEFT JOIN Subject s ON f.User_ID = s.User_ID
        GROUP BY f.User_ID, u.Name
        ORDER BY f.User_ID;
    "
    echo ""
    echo "✅ Done! Teachers should now have subjects assigned."
    echo ""
    echo "🔄 Restart the API to see changes:"
    echo "   docker-compose restart api"
else
    echo ""
    echo "❌ Error importing subjects. Check the error above."
    exit 1
fi

