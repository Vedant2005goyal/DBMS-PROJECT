#!/bin/bash

# Quick fix script to install face_recognition in running container
# This is a temporary fix - rebuild the image for permanent solution

echo "🔧 Installing face_recognition in running container..."
echo ""

# Check if container is running
if ! docker ps | grep -q attendance_api; then
    echo "❌ API container is not running!"
    echo "   Start it with: docker-compose up -d"
    exit 1
fi

echo "📦 Installing dlib and face_recognition..."
echo "   This may take several minutes as dlib needs to compile..."
echo ""

# Try to install using pre-built wheels first
docker exec attendance_api pip install --upgrade pip setuptools wheel

# Try installing dlib - this may fail but we'll handle it
echo "Installing dlib..."
docker exec attendance_api pip install dlib || {
    echo "⚠️  dlib installation failed. Trying alternative..."
    # Try with specific build flags
    docker exec attendance_api bash -c "pip install dlib --no-cache-dir" || {
        echo "❌ Could not install dlib. Face recognition will not work."
        echo "   You may need to rebuild the Docker image with updated Dockerfile."
        exit 1
    }
}

# Install face_recognition
echo "Installing face_recognition..."
docker exec attendance_api pip install face_recognition || {
    echo "❌ Could not install face_recognition."
    exit 1
}

echo ""
echo "✅ Face recognition modules installed!"
echo ""
echo "🔄 Restarting API container..."
docker-compose restart api

echo ""
echo "✅ Done! Face recognition should now work."
echo ""
echo "⚠️  Note: This is a temporary fix. For permanent solution, rebuild the image:"
echo "   docker-compose build --no-cache api"
echo "   docker-compose up -d"

