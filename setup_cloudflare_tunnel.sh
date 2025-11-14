#!/bin/bash

# Setup script for Cloudflare Tunnel (alternative to ngrok)
# This is less likely to be blocked by network security

echo "🚀 Setting up Cloudflare Tunnel for Attendance System"
echo ""

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared is not installed!"
    echo ""
    echo "📥 Install cloudflared:"
    echo "   macOS: brew install cloudflare/cloudflare/cloudflared"
    echo "   Or download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
    echo ""
    exit 1
fi

echo "✅ cloudflared is installed"
echo ""

# Check if API is running
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "⚠️  Warning: API server doesn't seem to be running on port 5001"
    echo "   Make sure Docker containers are running: docker-compose up -d"
    echo ""
fi

echo "🌐 Starting Cloudflare Tunnel..."
echo "   Local URL: http://localhost:5001"
echo "   Public URL: Will be shown below"
echo ""
echo "📝 Note: Keep this terminal open to maintain the tunnel"
echo "   Press Ctrl+C to stop"
echo ""
echo "✅ Advantages over ngrok:"
echo "   - Less likely to be blocked by network security"
echo "   - Free to use"
echo "   - Uses Cloudflare's infrastructure"
echo ""

# Start Cloudflare tunnel
cloudflared tunnel --url http://localhost:5001

