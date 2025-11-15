#!/bin/bash

# Quick Deployment Script for GSR Analytics
# Deploys to test server at 192.168.99.124

echo "========================================="
echo "GSR Analytics - Quick Deploy Script"
echo "========================================="
echo ""

# Create deployment package
echo "[1/4] Creating deployment package..."
tar -czf gsr-deploy.tar.gz \
  --exclude=node_modules \
  --exclude=.next \
  --exclude=__pycache__ \
  --exclude=*.pyc \
  --exclude=.git \
  --exclude=*.tar.gz \
  backend/ frontend/ docker-compose.yml docs/ prompts/ memory/ infra/ CLAUDE.md README.md QUICKSTART.md DEPLOY_MANUAL.md

echo "  Package created: gsr-deploy.tar.gz"
echo ""

# Copy to server
echo "[2/4] Copying to server..."
scp gsr-deploy.tar.gz silentoutlaw@192.168.99.124:~/
echo ""

# Extract on server
echo "[3/4] Extracting on server..."
ssh silentoutlaw@192.168.99.124 << 'ENDSSH'
mkdir -p /home/silentoutlaw/gsr-analytics
tar -xzf ~/gsr-deploy.tar.gz -C /home/silentoutlaw/gsr-analytics
cd /home/silentoutlaw/gsr-analytics
ENDSSH
echo ""

# Restart services
echo "[4/4] Restarting services..."
ssh silentoutlaw@192.168.99.124 << 'ENDSSH'
cd /home/silentoutlaw/gsr-analytics
docker-compose down
docker-compose up -d --build
ENDSSH

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Frontend: http://192.168.99.124:3000"
echo "Backend API: http://192.168.99.124:8000"
echo "API Docs: http://192.168.99.124:8000/api/docs"
echo ""
echo "To view logs:"
echo "  ssh silentoutlaw@192.168.99.124"
echo "  cd /home/silentoutlaw/gsr-analytics"
echo "  docker-compose logs -f"
echo ""
