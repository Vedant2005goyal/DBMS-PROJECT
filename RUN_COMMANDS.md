# Exact Commands to Run the Application

## Step 1: Clean Up (if needed)
```bash
cd /Users/vedantgoyal/Desktop/CODING/dbms_project
docker-compose down
docker system prune -f
```

## Step 2: Build and Start Containers
```bash
docker-compose up -d --build
```

## Step 3: Wait for Services to Start
```bash
# Wait 30 seconds for MySQL to initialize
sleep 30

# Check if containers are running
docker-compose ps
```

## Step 4: Check Logs (to see if everything is working)
```bash
# View all logs
docker-compose logs -f

# Or view specific service logs
docker-compose logs -f api
docker-compose logs -f mysql
```

## Step 5: Access the Application
Open your browser and go to:
```
http://localhost:5001
```

## Step 6: Test Login
Use these credentials from your CSV:
- **Email**: `vgoyal@thapar.edu`
- **Password**: `uf422ets@`

Or any other user from your CSV file.

## Troubleshooting Commands

### If containers fail to start:
```bash
# Check what's wrong
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d --build
```

### If you need to rebuild:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check if port 5001 is available:
```bash
lsof -i :5001
```

### View database:
```bash
# Connect to MySQL
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME}

# Or check if database exists
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} -e "SHOW DATABASES;"
```

### Stop the application:
```bash
docker-compose down
```

### Stop and remove all data (including database):
```bash
docker-compose down -v
```

