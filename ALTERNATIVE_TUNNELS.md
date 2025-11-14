# Alternative Tunneling Solutions

Since ngrok is being blocked by FortiGuard, here are alternatives:

## Option 1: Cloudflare Tunnel (Recommended - Free)

**Advantages:**
- ✅ Free
- ✅ Less likely to be blocked
- ✅ Uses Cloudflare's trusted infrastructure
- ✅ No account needed for basic use

**Setup:**
```bash
# Install
brew install cloudflare/cloudflare/cloudflared

# Start tunnel
./setup_cloudflare_tunnel.sh
# Or manually:
cloudflared tunnel --url http://localhost:5001
```

**Output:**
You'll get a URL like: `https://random-words-1234.trycloudflare.com`

## Option 2: LocalTunnel (Free)

**Advantages:**
- ✅ Free
- ✅ Simple to use
- ✅ npm-based

**Setup:**
```bash
# Install Node.js first if not installed
# Then:
npm install -g localtunnel

# Start tunnel
lt --port 5001
```

**Output:**
You'll get a URL like: `https://random-name.loca.lt`

## Option 3: Serveo (Free, SSH-based)

**Advantages:**
- ✅ Free
- ✅ No installation needed (uses SSH)
- ✅ Simple

**Setup:**
```bash
ssh -R 80:localhost:5001 serveo.net
```

**Note:** May require SSH key setup

## Option 4: ngrok Paid Plan

**Advantages:**
- ✅ Custom domain (less likely blocked)
- ✅ Static URL
- ✅ No warning page
- ✅ Professional

**Cost:** $8/month

**Setup:**
1. Upgrade at: https://dashboard.ngrok.com/billing
2. Configure custom domain
3. Use your own domain

## Option 5: Mobile Hotspot (Bypass Network)

**Quick fix:**
1. Turn on mobile hotspot
2. Connect computer to hotspot
3. Use existing ngrok URL
4. Bypasses FortiGuard entirely

## Comparison

| Service | Free | Blocked? | Setup Difficulty |
|---------|------|----------|------------------|
| Cloudflare Tunnel | ✅ | Less likely | Easy |
| LocalTunnel | ✅ | Sometimes | Easy |
| Serveo | ✅ | Sometimes | Medium |
| ngrok Free | ✅ | Often | Easy |
| ngrok Paid | ❌ | Rarely | Easy |

## Recommendation

**For immediate use:** Cloudflare Tunnel
- Free
- Less likely to be blocked
- Easy setup

**For production:** ngrok Paid Plan
- Custom domain
- Professional
- Reliable

## Quick Start: Cloudflare Tunnel

```bash
# 1. Install
brew install cloudflare/cloudflare/cloudflared

# 2. Start tunnel
./setup_cloudflare_tunnel.sh

# 3. Copy the URL it gives you
# 4. Access from anywhere!
```

