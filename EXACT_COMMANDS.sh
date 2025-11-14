#!/bin/bash
# Exact commands to run the application

echo "=== Step 1: Cleaning up (if needed) ==="
docker-compose down 2>/dev/null
echo "✓ Cleaned up"

echo ""
echo "=== Step 2: Building and starting containers ==="
docker-compose up -d --build

echo ""
echo "=== Step 3: Waiting for services to initialize (30 seconds) ==="
sleep 30

echo ""
echo "=== Step 4: Checking container status ==="
docker-compose ps

echo ""
echo "=== Step 5: Viewing API logs (press Ctrl+C to exit) ==="
echo "If you see 'Running on http://0.0.0.0:5000', the API is ready!"
echo ""
docker-compose logs api | tail -20

echo ""
echo "=== ✅ Application should now be running! ==="
echo "🌐 Open your browser and go to: http://localhost:5001"
echo ""
echo "📝 Test login credentials:"
echo "   Email: vgoyal@thapar.edu"
echo "   Password: uf422ets@"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
