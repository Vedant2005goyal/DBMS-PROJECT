# How to See UI Updates

## Quick Fix (Choose One):

### Option 1: Rebuild Docker Image (Recommended)
Since the frontend files are copied into the Docker image during build, you need to rebuild:

```bash
docker-compose down
docker-compose build --no-cache api
docker-compose up -d
```

### Option 2: Add Volume Mount (Already Done!)
I've updated `docker-compose.yml` to mount the frontend directory. Now restart:

```bash
docker-compose restart api
```

### Option 3: Clear Browser Cache
Even after updating files, your browser might be caching the old version:

**Safari:**
1. Press `Cmd + Option + E` to empty caches
2. Or go to Safari → Preferences → Advanced → Check "Show Develop menu"
3. Then Develop → Empty Caches
4. Hard refresh: `Cmd + Shift + R`

**Chrome/Firefox:**
- Hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
- Or open DevTools (F12) → Right-click refresh button → "Empty Cache and Hard Reload"

## Verify Changes:

1. **Check the file was updated:**
   ```bash
   grep -n "Enhanced Navbar" frontend/teacher_dashboard.html
   ```
   Should show line numbers if the new UI is there.

2. **Check Docker is serving the right file:**
   ```bash
   docker exec attendance_api cat /app/frontend/teacher_dashboard.html | head -20
   ```

3. **Open browser DevTools (F12) and check:**
   - Network tab → Disable cache
   - Reload the page
   - Check if the HTML has the new styles

## If Still Not Working:

1. **Stop and rebuild completely:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Check if frontend is mounted:**
   ```bash
   docker exec attendance_api ls -la /app/frontend/
   ```

3. **Directly edit in container (temporary test):**
   ```bash
   docker exec -it attendance_api bash
   # Then check the file
   cat /app/frontend/teacher_dashboard.html | head -50
   ```

