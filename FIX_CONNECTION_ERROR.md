# Fix Connection Error with Ngrok

## The Problem

When accessing your app via ngrok URL (e.g., `https://gymnanthous-dayle-waxy.ngrok-free.dev`), you see:
- "Connection error. Is the server running on port 5001?"

## Why This Happens

The frontend was hardcoded to use `http://localhost:5001`, which:
- ❌ Doesn't work when accessed via ngrok (different domain)
- ❌ Causes CORS errors
- ❌ Can't connect from external networks

## The Fix

I've updated all frontend files to **auto-detect** the API URL:

1. **If accessed via ngrok/cloudflare tunnel**: Uses the same domain
2. **If accessed via localhost**: Uses `http://localhost:5001`

## What Was Changed

Updated files:
- ✅ `frontend/index.html` - Login page
- ✅ `frontend/teacher_dashboard.html` - Teacher dashboard
- ✅ `frontend/student_dashboard.html` - Student dashboard

All now auto-detect the correct API URL based on where they're accessed from.

## How to Test

### 1. Restart Docker (to load updated frontend)
```bash
docker-compose restart api
```

### 2. Clear Browser Cache
- Safari: `Cmd + Option + E` then `Cmd + Shift + R`
- Chrome: `Cmd + Shift + R`

### 3. Access via Ngrok
1. Visit: `https://gymnanthous-dayle-waxy.ngrok-free.dev`
2. Click "Visit Site" (if FortiGuard warning appears)
3. Open browser console (F12)
4. Check console - should see: `🌐 API URL: https://gymnanthous-dayle-waxy.ngrok-free.dev`
5. Try logging in - should work now!

### 4. Access via Localhost (Still Works)
1. Visit: `http://localhost:5001`
2. Should see: `🌐 API URL: http://localhost:5001`
3. Works as before

## Verification

**Check browser console (F12):**
- Should see: `🌐 API URL: [your-url]`
- No CORS errors
- API calls should succeed

**Test login:**
- Use: `dwashington@thapar.edu` / `passDWa3%^`
- Should redirect to teacher dashboard
- Subjects should load

## Troubleshooting

### Still seeing connection error?

1. **Check Docker is running:**
   ```bash
   docker-compose ps
   ```
   Should show `attendance_api` as "Up"

2. **Check API is accessible:**
   ```bash
   curl http://localhost:5001/api/login -X POST -H "Content-Type: application/json" -d '{"email":"test","password":"test"}'
   ```
   Should return JSON response

3. **Check browser console:**
   - Open DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

4. **Verify frontend files updated:**
   ```bash
   grep -n "getAPIUrl" frontend/index.html
   ```
   Should show the function

5. **Clear browser cache completely:**
   - Safari: Preferences → Privacy → Manage Website Data → Remove All
   - Or use private/incognito window

### CORS Errors?

The Flask app already has CORS enabled. If you still see CORS errors:
1. Check `backend/api.py` has `CORS(app)`
2. Restart Docker: `docker-compose restart api`

## How It Works

The frontend now uses this logic:

```javascript
const getAPIUrl = () => {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    
    // If accessing via tunnel (ngrok, cloudflare, etc.)
    if (hostname.includes('ngrok') || 
        hostname.includes('cloudflare') || 
        hostname !== 'localhost') {
        return `${protocol}//${hostname}`;
    }
    
    // Default to localhost
    return 'http://localhost:5001';
};
```

This automatically:
- ✅ Uses ngrok URL when accessed via ngrok
- ✅ Uses localhost when accessed locally
- ✅ Works with any tunnel service (Cloudflare, LocalTunnel, etc.)

## Summary

✅ **Fixed**: Frontend now auto-detects API URL
✅ **Works**: Both localhost and ngrok access
✅ **No config needed**: Automatically adapts

**Next steps:**
1. Restart Docker: `docker-compose restart api`
2. Clear browser cache
3. Access via ngrok URL
4. Check console for `🌐 API URL` message
5. Login should work!

