# Deployment Guide

Complete guide for deploying GSR Analytics to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [VM Deployment](#vm-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- Docker 20.10+ and Docker Compose 2.0+
- Git
- At least 4GB RAM, 20GB disk space
- API Keys (see Configuration section)

### Recommended
- Linux (Ubuntu 22.04 LTS) or similar
- SSL certificate (Let's Encrypt)
- Domain name

---

## Local Development

### 1. Clone Repository

```bash
git clone <repository-url>
cd gold-silver-ratio
```

### 2. Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit with your API keys
nano backend/.env
```

Required API keys:
- `FRED_API_KEY` - Get free at https://fred.stlouisfed.org/docs/api/api_key.html
- At least ONE of: `ALPHA_VANTAGE_API_KEY`, `METALS_API_KEY`
- At least ONE of: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Backfill historical data (5 years)
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import backfill_historical_data
asyncio.run(backfill_historical_data(years=5))
"

# Compute initial metrics
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
asyncio.run(compute_all_metrics())
"
```

### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## VM Deployment (Ubuntu 22.04)

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install git
sudo apt install git -y
```

### 2. Clone and Configure

```bash
cd /opt
sudo git clone <repository-url> gsr-analytics
cd gsr-analytics
sudo chown -R $USER:$USER .

# Configure environment
cp backend/.env.example backend/.env
nano backend/.env
```

### 3. Configure Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if not already)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

### 4. Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot -y

# Get certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 5. Update Nginx Configuration

Edit `infra/nginx/nginx.conf` to use your domain and SSL certificates:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of config
}
```

### 6. Start Services

```bash
# Build and start
docker-compose up -d --build

# Initialize database
docker-compose exec backend alembic upgrade head

# Backfill data
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import backfill_historical_data
asyncio.run(backfill_historical_data(years=5))
"
```

### 7. Setup Systemd Service (Optional)

Create `/etc/systemd/system/gsr-analytics.service`:

```ini
[Unit]
Description=GSR Analytics Docker Compose
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/gsr-analytics
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable gsr-analytics
sudo systemctl start gsr-analytics
```

---

## AWS Deployment

### Option 1: EC2 + RDS

#### 1. Launch EC2 Instance

- **Instance Type**: t3.medium (2 vCPU, 4GB RAM) or larger
- **AMI**: Ubuntu 22.04 LTS
- **Storage**: 30GB GP3
- **Security Group**:
  - Port 22 (SSH) from your IP
  - Port 80 (HTTP) from 0.0.0.0/0
  - Port 443 (HTTPS) from 0.0.0.0/0

#### 2. Create RDS PostgreSQL Instance

- **Engine**: PostgreSQL 15
- **Instance Class**: db.t3.micro (for small workload)
- **Storage**: 20GB GP3
- **Enable**: Automated backups, Multi-AZ (for production)
- **Security Group**: Allow port 5432 from EC2 security group

#### 3. Configure EC2

SSH into EC2 and follow [VM Deployment](#vm-deployment) steps, but update `DATABASE_URL`:

```bash
# In backend/.env
DATABASE_URL=postgresql+asyncpg://username:password@rds-endpoint:5432/gsr_analytics
```

#### 4. Setup CloudWatch Logs (Optional)

Install CloudWatch agent for log monitoring:

```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
```

#### 5. Setup S3 for Backups

```bash
# Install AWS CLI
sudo apt install awscli -y

# Configure backup script
cat > /opt/gsr-analytics/backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U gsr_user gsr_analytics | gzip > backup_$TIMESTAMP.sql.gz
aws s3 cp backup_$TIMESTAMP.sql.gz s3://your-backup-bucket/
rm backup_$TIMESTAMP.sql.gz
EOF

chmod +x /opt/gsr-analytics/backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/gsr-analytics/backup.sh" | crontab -
```

### Option 2: ECS Fargate (Fully Managed)

Requires converting docker-compose to ECS task definitions. See AWS ECS documentation for details.

---

## Configuration

### Environment Variables

Critical settings in `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Data Providers (at least one each required)
FRED_API_KEY=your_fred_key
ALPHA_VANTAGE_API_KEY=your_av_key  # OR METALS_API_KEY

# AI (at least one required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Ingestion Schedule
INGESTION_SCHEDULE_ENABLED=true
INGESTION_DAILY_HOUR=20  # UTC
INGESTION_TIMEZONE=UTC

# Alerts (optional)
ALERT_EMAIL_ENABLED=false
ALERT_WEBHOOK_ENABLED=false
```

### Nginx Reverse Proxy

Edit `infra/nginx/nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring

### Application Health

```bash
# Check service health
curl http://localhost:8000/health

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f worker
```

### Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U gsr_user -d gsr_analytics

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check TimescaleDB hypertables
SELECT * FROM timescaledb_information.hypertables;
```

### Prometheus + Grafana (Optional)

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  volumes:
    - grafana_data:/var/lib/grafana
```

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database connection - verify DATABASE_URL
# 2. Missing API keys - check .env file
# 3. Port conflicts - ensure ports 8000, 5432 are free
```

### Data Ingestion Fails

```bash
# Manual test
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import ingest_all_data
result = asyncio.run(ingest_all_data(days_back=1))
print(result)
"

# Check API keys
docker-compose exec backend python -c "
from app.core.config import settings
print('FRED key:', settings.fred_api_key[:10] if settings.fred_api_key else 'MISSING')
print('AV key:', settings.alpha_vantage_api_key[:10] if settings.alpha_vantage_api_key else 'MISSING')
"
```

### Frontend Connection Errors

```bash
# Check backend is accessible
curl http://localhost:8000/health

# Check CORS settings in backend/.env
CORS_ORIGINS=["http://localhost:3000"]

# Check frontend API URL
# In frontend, it should point to: http://localhost:8000/api/v1
```

### Database Migration Issues

```bash
# Check current version
docker-compose exec backend alembic current

# Force to specific version
docker-compose exec backend alembic downgrade <revision>
docker-compose exec backend alembic upgrade head

# Reset database (CAUTION: destroys data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase resources if needed (in docker-compose.yml):
services:
  postgres:
    mem_limit: 2g
    cpus: 2
```

---

## Maintenance

### Regular Tasks

**Daily** (Automated):
- Data ingestion runs at configured time
- Metric computation
- Alert checking

**Weekly**:
- Review logs for errors
- Check disk space usage
- Review alert accuracy

**Monthly**:
- Database backups verification
- Update dependencies (security patches)
- Review and optimize database indexes

### Updates

```bash
# Pull latest code
cd /opt/gsr-analytics
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run new migrations
docker-compose exec backend alembic upgrade head
```

---

## Security Checklist

- [ ] All API keys in environment variables (not committed)
- [ ] SSL/TLS enabled (HTTPS)
- [ ] Firewall configured (only 80, 443, 22 open)
- [ ] Database password is strong and unique
- [ ] Regular backups configured
- [ ] Logs are monitored
- [ ] Dependencies are up-to-date
- [ ] Non-root users in containers
- [ ] Rate limiting enabled on nginx

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check GitHub Issues
4. Contact: [your-email]

**Remember**: This software is for educational purposes. Not investment advice.
