# Deployment Guide

## Local Deployment

### Step 1: Environment Setup

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   - Set a strong `DB_PASSWORD`
   - Configure email credentials (for notifications)
   - Adjust other settings as needed

### Step 2: Deploy with Docker

**Option A: Using the deployment script**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Option B: Manual deployment**
```bash
# Build and start containers
docker-compose up -d --build

# Wait for database initialization
sleep 20

# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 3: Initialize Database

The database schema should be automatically initialized from `schema.sql`. If not:

```bash
# Access MySQL container
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME}

# Or import schema manually
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < schema.sql
```

### Step 4: Hash Passwords for Users

If you need to update user passwords in the database:

```bash
# Hash a password
python hash_password.py "your_password_here"

# Then update in database
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} -e "UPDATE User SET Password_Hash = 'hashed_value_here' WHERE Email = 'user@example.com';"
```

### Step 5: Access the Application

- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api
- **MySQL**: localhost:3306

## Server Deployment

### Prerequisites

- Server with Docker and Docker Compose installed
- At least 4GB RAM
- Domain name (optional, for production)

### Steps

1. **Clone repository on server:**
   ```bash
   git clone <your-repo-url>
   cd dbms_project
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```

3. **Deploy:**
   ```bash
   ./deploy.sh
   ```

4. **Set up reverse proxy (Nginx example):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Set up SSL (Let's Encrypt):**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Troubleshooting

### Containers won't start

```bash
# Check logs
docker-compose logs

# Restart containers
docker-compose restart

# Rebuild if needed
docker-compose up -d --build --force-recreate
```

### Database connection errors

1. Ensure MySQL container is running:
   ```bash
   docker-compose ps mysql
   ```

2. Check database credentials in `.env`

3. Wait longer for MySQL to initialize (can take 30+ seconds)

### Port conflicts

If port 5000 is in use, modify `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Use different host port
```

### Face recognition not working

1. Ensure `student_photos` directory exists:
   ```bash
   mkdir -p student_photos
   chmod 755 student_photos
   ```

2. Register student faces first using the registration endpoint

3. Check camera permissions in browser

## Maintenance

### Backup Database

```bash
docker-compose exec mysql mysqldump -u root -p${DB_PASSWORD} ${DB_NAME} > backup.sql
```

### Restore Database

```bash
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < backup.sql
```

### Update Application

```bash
git pull
docker-compose up -d --build
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f scheduler
docker-compose logs -f mysql
```

### Stop Application

```bash
docker-compose down
```

### Remove Everything (including data)

```bash
docker-compose down -v
```

## Production Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Use strong database passwords
- [ ] Configure proper email SMTP settings
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Review and update security settings
- [ ] Test all functionality
- [ ] Set up domain name and DNS

