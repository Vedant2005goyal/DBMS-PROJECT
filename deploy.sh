#!/bin/bash

echo "=== Attendance System Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "Please edit .env with your credentials"
    exit 1
fi

# Load environment variables from .env
export $(grep -v '^#' .env | xargs)

# Build and start containers
echo "Building Docker containers..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Waiting for database to be fully ready..."
sleep 15

echo "Running database migrations..."
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < schema.sql 2>/dev/null || {
    echo "Note: Database may already be initialized or schema.sql will be auto-loaded. Continuing..."
}

echo "=== Deployment Complete ==="
echo "API running at: http://localhost:5001"
echo "Check logs with: docker-compose logs -f"

