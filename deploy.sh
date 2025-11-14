#!/bin/bash

echo "=== Attendance System Deployment ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "Please edit .env with your credentials"
    exit 1
fi

# Build and start containers
echo "Building Docker containers..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < schema.sql

echo "=== Deployment Complete ==="
echo "API running at: http://localhost:5000"
echo "Check logs with: docker-compose logs -f"

