#!/bin/bash

# Quick script to start all services and verify they're running

echo "🚀 Starting Attendance System Services"
echo ""

# Start all services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 Verifying API is accessible..."
if curl -s http://127.0.0.1:5001 > /dev/null; then
    echo "✅ API is running on http://127.0.0.1:5001"
else
    echo "❌ API is not accessible. Check logs: docker-compose logs api"
fi

echo ""
echo "✅ Services started!"
echo ""
echo "🌐 Access your app at: http://localhost:5001"
echo ""
echo "📝 To start Cloudflare tunnel:"
echo "   ./setup_cloudflare_tunnel.sh"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f api"

