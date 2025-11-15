#!/bin/bash

# Deployment script for test server at 192.168.99.124
# Usage: ./deploy-to-test.sh

SERVER="192.168.99.124"
USER="silentoutlaw"
REMOTE_DIR="/home/silentoutlaw/gsr-analytics"

echo "=== GSR Analytics - Deploy to Test Server ==="
echo "Server: $SERVER"
echo "User: $USER"
echo ""

# Create tarball of the project
echo "Creating deployment package..."
tar -czf gsr-deploy.tar.gz \
  --exclude=node_modules \
  --exclude=.next \
  --exclude=__pycache__ \
  --exclude=*.pyc \
  --exclude=.git \
  --exclude=gsr-analytics.tar.gz \
  --exclude=gsr-deploy.tar.gz \
  backend/ frontend/ docker-compose.yml docs/ prompts/ memory/ infra/ CLAUDE.md README.md QUICKSTART.md

echo "Package created: gsr-deploy.tar.gz"
echo ""
echo "Next steps (manual):"
echo "1. Copy package to server:"
echo "   scp gsr-deploy.tar.gz $USER@$SERVER:~/"
echo ""
echo "2. SSH to server and extract:"
echo "   ssh $USER@$SERVER"
echo "   mkdir -p $REMOTE_DIR"
echo "   tar -xzf gsr-deploy.tar.gz -C $REMOTE_DIR"
echo "   cd $REMOTE_DIR"
echo ""
echo "3. Set up environment:"
echo "   cp backend/.env.example backend/.env"
echo "   # Edit backend/.env with API keys"
echo ""
echo "4. Start services:"
echo "   docker-compose up -d"
echo ""
echo "5. Initialize database:"
echo "   docker-compose exec backend alembic upgrade head"
echo ""
echo "6. Test the deployment:"
echo "   curl http://$SERVER:8000/health"
echo "   curl http://$SERVER:3000"
