# Ngrok Setup Guide

## What is Ngrok?

Ngrok creates a secure tunnel from the internet to your local development server, allowing you to:
- Access your app from anywhere (mobile, other computers)
- Test webhooks from external services
- Share your app with others without deploying

## Installation

### macOS (using Homebrew)
```bash
brew install ngrok/ngrok/ngrok
```

### Manual Installation
1. Go to https://ngrok.com/download
2. Download for your OS
3. Extract and add to PATH, or use the full path

### Sign Up (Free)
1. Go to https://dashboard.ngrok.com/signup
2. Sign up for a free account
3. Get your authtoken from the dashboard

## Setup Steps

### 1. Authenticate ngrok
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```
(Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken)

### 2. Start your Docker containers
```bash
docker-compose up -d
```

### 3. Start ngrok tunnel

**Option A: Use the setup script**
```bash
chmod +x setup_ngrok.sh
./setup_ngrok.sh
```

**Option B: Manual command**
```bash
ngrok http 5001
```

### 4. Access your app

After starting ngrok, you'll see output like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:5001
```

Use the `https://` URL to access your app from anywhere!

## Important Notes

### Free Tier Limitations
- **Session timeout**: Free tunnels expire after 2 hours
- **Random URLs**: Each time you restart, you get a new URL
- **Rate limits**: Limited requests per minute

### Paid Plans
If you need:
- Static domains (same URL every time)
- No session timeouts
- Higher rate limits
- Custom domains

Upgrade at https://dashboard.ngrok.com/billing

## Troubleshooting

### "ngrok: command not found"
- Make sure ngrok is installed and in your PATH
- Or use full path: `/path/to/ngrok http 5001`

### "Tunnel not found"
- Make sure your Docker containers are running
- Check that port 5001 is accessible: `curl http://localhost:5001`

### "Connection refused"
- Verify API is running: `docker-compose ps`
- Check logs: `docker-compose logs api`

### CORS Issues
The Flask app already has CORS enabled, so this should work. If you see CORS errors:
- Check `backend/api.py` has `CORS(app)`
- Verify the ngrok URL is using HTTPS

## Web Interface

Ngrok provides a web interface to inspect requests:
- Default: http://localhost:4040
- View all requests, responses, and replay them

## Security

⚠️ **Important**: 
- Don't share your ngrok URL publicly if it contains sensitive data
- Free tier URLs are discoverable
- Use environment variables for sensitive config
- Consider using ngrok's IP restrictions for production

## Example Usage

1. Start Docker:
   ```bash
   docker-compose up -d
   ```

2. Start ngrok:
   ```bash
   ngrok http 5001
   ```

3. Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

4. Access from anywhere:
   - Desktop: Open in browser
   - Mobile: Use the ngrok URL
   - Share with team members

5. View requests:
   - Open http://localhost:4040 in browser
   - See all API calls in real-time

## Stopping

Press `Ctrl+C` in the terminal where ngrok is running, or:
```bash
pkill ngrok
```

