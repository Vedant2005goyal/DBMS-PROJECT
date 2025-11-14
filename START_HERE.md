# 🚀 START HERE - Exact Commands to Run

## Quick Start (Automated)

Run this single command:
```bash
cd /Users/vedantgoyal/Desktop/CODING/dbms_project
./EXACT_COMMANDS.sh
```

## Manual Steps (If you prefer)

### 1. Navigate to project directory
```bash
cd /Users/vedantgoyal/Desktop/CODING/dbms_project
```

### 2. Clean up any existing containers
```bash
docker-compose down
```

### 3. Build and start all services
```bash
docker-compose up -d --build
```

### 4. Wait for services to initialize (30 seconds)
```bash
sleep 30
```

### 5. Check if containers are running
```bash
docker-compose ps
```

You should see 3 containers:
- `attendance_db` (MySQL) - Status: Up
- `attendance_api` (Flask API) - Status: Up  
- `attendance_scheduler` (Scheduler) - Status: Up

### 6. Check API logs to confirm it's running
```bash
docker-compose logs api | tail -20
```

Look for: `Running on http://0.0.0.0:5000`

### 7. Open your browser
Go to: **http://localhost:5001**

### 8. Login with test credentials
- **Email**: `vgoyal@thapar.edu`
- **Password**: `uf422ets@`

## ✅ Success Indicators

- All 3 containers show "Up" status
- API logs show "Running on http://0.0.0.0:5000"
- Browser loads the login page at http://localhost:5001
- You can successfully log in

## 🔍 Troubleshooting

### If build fails:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### If containers won't start:
```bash
docker-compose logs
```

### If port 5001 is busy:
```bash
lsof -i :5001
# Kill the process or change port in docker-compose.yml
```

### View all logs:
```bash
docker-compose logs -f
```

### Stop everything:
```bash
docker-compose down
```

## 📝 Next Steps After Login

1. You'll be redirected to the Student Dashboard
2. Click "Mark Attendance" to test face recognition
3. View your attendance statistics on the dashboard

