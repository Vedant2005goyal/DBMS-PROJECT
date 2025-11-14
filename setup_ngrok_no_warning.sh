#!/bin/bash

# Setup script for ngrok tunnel without warning page
# This uses ngrok's --host-header option to bypass the warning

echo "🚀 Setting up ngrok tunnel (no warning page)"
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

echo "🌐 Starting ngrok tunnel (bypassing warning page)..."
echo "   Local URL: http://localhost:5001"
echo "   Public URL: Will be shown below"
echo ""
echo "📝 Note: Keep this terminal open to maintain the tunnel"
echo "   Press Ctrl+C to stop"
echo ""

# Start ngrok with host header rewrite to bypass warning
ngrok http 5001 --host-header=rewrite

