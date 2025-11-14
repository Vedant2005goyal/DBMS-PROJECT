#!/bin/bash

# Setup script for ngrok tunnel
# This script helps you expose your local Flask app to the internet

echo "🚀 Setting up ngrok tunnel for Attendance System"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed!"
    echo ""
    echo "📥 Install ngrok:"
    echo "   macOS: brew install ngrok/ngrok/ngrok"
    echo "   Or download from: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "✅ ngrok is installed"
echo ""

# Check if API is running
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "⚠️  Warning: API server doesn't seem to be running on port 5001"
    echo "   Make sure Docker containers are running: docker-compose up -d"
    echo ""
fi

echo "🌐 Starting ngrok tunnel..."
echo "   Local URL: http://localhost:5001"
echo "   Public URL: Will be shown below"
echo ""
echo "📝 Note: Keep this terminal open to maintain the tunnel"
echo "   Press Ctrl+C to stop"
echo ""

# Start ngrok tunnel
# Note: Free tier shows a warning page - this is normal
# Users need to click "Visit Site" to proceed
ngrok http 5001

