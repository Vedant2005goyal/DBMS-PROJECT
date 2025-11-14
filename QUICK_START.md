# Quick Start Guide

## Port Changed to 5001

**Important**: The application now runs on port **5001** instead of 5000 (since port 5000 is used by macOS).

## Deployment Steps

### 1. Configure Environment

Make sure your `.env` file is set up:

```bash
# If .env doesn't exist, it will be created from .env.example
cp .env.example .env
# Edit .env with your settings
```

### 2. Deploy

```bash
./deploy.sh
```

Or manually:

```bash
docker-compose up -d --build
```

### 3. Access Application

- **Frontend**: http://localhost:5001
- **API**: http://localhost:5001/api

### 4. Check Status

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f mysql
```

## Troubleshooting

### Containers not starting

```bash
# Check logs
docker-compose logs

# Restart
docker-compose restart

# Rebuild and restart
docker-compose up -d --build --force-recreate
```

### Database connection issues

Wait 30-60 seconds after starting for MySQL to fully initialize.

### Port 5001 also in use?

Edit `docker-compose.yml` and change:
```yaml
ports:
  - "5002:5000"  # Change 5002 to any available port
```

Then update all frontend files to use the new port.

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

## Stop Application

```bash
docker-compose down
```

## Common Issues

1. **"Port already in use"**: Change the port in docker-compose.yml
2. **"Database connection failed"**: Wait longer for MySQL to start
3. **"Cannot connect to API"**: Check if containers are running with `docker-compose ps`

