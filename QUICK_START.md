# Quick Start Guide

## Fix Subjects Issue & Setup Ngrok

### Step 1: Restart API to Load Fixed Code
```bash
docker-compose restart api
```

### Step 2: Check Subjects in Database
```bash
# Option A: Run the Python script
python3 check_subjects.py

# Option B: Check via Docker
docker exec attendance_db mysql -u root -p${DB_PASSWORD} attendance_system -e "SELECT Subject_ID, Subject_Name, Subject_Code, User_ID FROM Subject WHERE User_ID = 3;"
```

### Step 3: Verify API is Working
Open browser console (F12) and check:
- Network tab → Look for `/api/teacher/subjects?teacher_id=3`
- Console tab → Should see debug logs

### Step 4: Clear Browser Cache
**Safari:**
- `Cmd + Option + E` (empty caches)
- `Cmd + Shift + R` (hard refresh)

### Step 5: Setup Ngrok

#### Install ngrok (if not installed):
```bash
# macOS
brew install ngrok/ngrok/ngrok

# Or download from https://ngrok.com/download
```

#### Authenticate (first time only):
```bash
# Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

#### Start ngrok tunnel:
```bash
# Option A: Use the script
./setup_ngrok.sh

# Option B: Manual
ngrok http 5001
```

#### Access your app:
After starting ngrok, you'll see:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:5001
```

Use the `https://` URL to access from anywhere!

## Troubleshooting Subjects

If subjects still don't show:

1. **Check database directly:**
   ```bash
   docker exec attendance_db mysql -u root -p${DB_PASSWORD} attendance_system -e "SELECT * FROM Subject WHERE User_ID = 3;"
   ```

2. **Check API logs:**
   ```bash
   docker-compose logs api | grep -i subject
   ```

3. **Verify teacher login:**
   - Use: `dwashington@thapar.edu` / `passDWa3%^` (User_ID: 3)
   - Should have 5 subjects assigned

4. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for API response

## Expected Subjects for Teachers

- **User_ID 3 (Denzel Washington):** 5 subjects
  - Introduction to Programming (UCS101)
  - Data Structures (UCS310)
  - Operating Systems (UCS410)
  - Software Engineering (UCS511)
  - Surveying (UCE310)

- **User_ID 7 (Kate Winslet):** 6 subjects
- **User_ID 16 (Tom Hanks):** 8 subjects

## Ngrok Web Interface

View all requests in real-time:
- Open: http://localhost:4040
- See API calls, responses, replay requests

## Stop Ngrok

Press `Ctrl+C` in the terminal where ngrok is running.

