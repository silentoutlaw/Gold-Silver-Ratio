# Manual Deployment to Test Server

## Server Details
- **IP**: 192.168.99.124
- **User**: silentoutlaw
- **Password**: hyRule-penneewarp
- **Deploy Directory**: /home/silentoutlaw/gsr-analytics

## Quick Deploy Steps

### 1. Copy Package to Server
```bash
scp gsr-deploy.tar.gz silentoutlaw@192.168.99.124:~/
```

### 2. SSH to Server
```bash
ssh silentoutlaw@192.168.99.124
# Password: hyRule-penneewarp
```

### 3. Extract and Setup
```bash
mkdir -p /home/silentoutlaw/gsr-analytics
tar -xzf ~/gsr-deploy.tar.gz -C /home/silentoutlaw/gsr-analytics
cd /home/silentoutlaw/gsr-analytics
```

### 4. Configure Environment
```bash
# Backend
cp backend/.env.example backend/.env
nano backend/.env  # Add your API keys

# Frontend
nano frontend/.env.local  # Add: NEXT_PUBLIC_API_URL=http://192.168.99.124:8000/api/v1
```

### 5. Start Services
```bash
docker-compose up -d
```

### 6. Initialize Database
```bash
docker-compose exec backend alembic upgrade head
```

### 7. Run Initial Data Ingestion
```bash
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import ingest_all_data
result = asyncio.run(ingest_all_data(days_back=30))
print(result)
"
```

### 8. Compute Initial Metrics
```bash
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
result = asyncio.run(compute_all_metrics())
print(result)
"
```

### 9. Test Deployment
```bash
# Test backend
curl http://192.168.99.124:8000/health
curl http://192.168.99.124:8000/api/v1/metrics/gsr/current

# Test frontend (in browser)
# http://192.168.99.124:3000
```

## Updating After Code Changes

```bash
# On local machine: recreate package
python deploy.py  # or manually: tar -czf gsr-deploy.tar.gz ...

# Copy to server
scp gsr-deploy.tar.gz silentoutlaw@192.168.99.124:~/

# On server
cd /home/silentoutlaw/gsr-analytics
docker-compose down
cd ~
tar -xzf ~/gsr-deploy.tar.gz -C /home/silentoutlaw/gsr-analytics
cd /home/silentoutlaw/gsr-analytics
docker-compose up -d --build
```

## Viewing Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs --tail=100
```

## Stopping Services
```bash
docker-compose down
```

## Package Already Created
The deployment package `gsr-deploy.tar.gz` (41MB) is ready to deploy!
