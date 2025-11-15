# 🚀 Quick Start Guide

Get GSR Analytics up and running in 5 minutes!

## Prerequisites

✅ Docker Desktop installed and running
✅ Git installed
✅ At least 4GB free RAM
✅ API keys ready (see below)

---

## Required API Keys (Get Free)

### 1. FRED API Key (Required)
📍 Get at: https://fred.stlouisfed.org/docs/api/api_key.html
- Takes 2 minutes
- Completely free
- Provides macro economic data

### 2. Metals Price API (Pick ONE)
Option A: **Alpha Vantage** (Recommended)
- 📍 Get at: https://www.alphavantage.co/support/#api-key
- Free tier: 25 calls/day
- Good for testing

Option B: **Metals-API**
- 📍 Get at: https://metals-api.com
- Free tier: 50 calls/month
- Good for production

### 3. AI Provider (Pick ONE)
Option A: **OpenAI** (Recommended)
- 📍 Get at: https://platform.openai.com/api-keys
- Pay-as-you-go
- Best performance

Option B: **Anthropic (Claude)**
- 📍 Get at: https://console.anthropic.com/
- Good alternative

Option C: **Google (Gemini)**
- 📍 Get at: https://makersuite.google.com/app/apikey
- Free tier available

---

## Step-by-Step Setup

### 1️⃣ Clone Repository

```bash
# Navigate to your projects folder
cd ~/projects  # or wherever you keep projects

# Clone the repository
git clone <repository-url> gsr-analytics
cd gsr-analytics
```

### 2️⃣ Configure API Keys

```bash
# Copy the template
cp backend/.env.example backend/.env

# Open in your editor
# Windows: notepad backend/.env
# Mac/Linux: nano backend/.env
```

**Edit backend/.env** and add your API keys:

```bash
# Required
FRED_API_KEY=your_fred_key_here

# Pick ONE metals API
ALPHA_VANTAGE_API_KEY=your_av_key_here
# OR
METALS_API_KEY=your_metals_key_here

# Pick ONE AI provider
OPENAI_API_KEY=your_openai_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
GOOGLE_API_KEY=your_google_key_here
```

Save and close the file.

### 3️⃣ Start Services

```bash
# Start all services (backend, frontend, database)
docker-compose up -d

# This will:
# - Download required Docker images (first time only)
# - Start PostgreSQL database
# - Start Redis cache
# - Start backend API
# - Start frontend web app
# - Start worker for scheduled jobs
# - Start Nginx reverse proxy

# Wait about 30 seconds for everything to start
```

### 4️⃣ Initialize Database

```bash
# Run database migrations (creates tables)
docker-compose exec backend alembic upgrade head

# You should see output like:
# INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial database schema
```

### 5️⃣ Fetch Historical Data

```bash
# Fetch 5 years of historical data
# This takes 5-10 minutes depending on API rate limits
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import backfill_historical_data
print('Starting historical data backfill...')
result = asyncio.run(backfill_historical_data(years=5))
print('Done!', result)
"
```

You'll see progress messages like:
```
Fetched 1825 FRED data points
Fetched 1825 metals price points
Fetched 1825 Yahoo Finance data points
...
```

### 6️⃣ Compute Metrics

```bash
# Calculate GSR, z-scores, percentiles, correlations
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
print('Computing metrics...')
result = asyncio.run(compute_all_metrics())
print('Done!', result)
"
```

---

## 🎉 You're Done!

### Access the Application

Open your browser and go to:

🌐 **http://localhost:3000**

You should see:
- Current GSR value
- GSR percentile and z-score
- Active trading signals (if GSR is at extremes)
- Gold and silver prices

### Backend API

📊 **API Docs**: http://localhost:8000/api/docs

Try it out:
- Click on any endpoint
- Click "Try it out"
- Click "Execute"

### Check Logs

```bash
# View all logs
docker-compose logs -f

# View just backend
docker-compose logs -f backend

# View just frontend
docker-compose logs -f frontend
```

---

## 📊 Daily Operations

### Data Updates (Automatic)

The system automatically:
- ✅ Fetches new data daily at 8 PM UTC
- ✅ Computes metrics 5 minutes later
- ✅ Generates signals 10 minutes later
- ✅ Checks alerts every hour

No manual intervention needed!

### Manual Data Refresh

If you want to fetch data immediately:

```bash
# Fetch today's data
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import ingest_all_data
result = asyncio.run(ingest_all_data(days_back=1))
print(result)
"

# Compute metrics
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
result = asyncio.run(compute_all_metrics())
print(result)
"
```

### View Current GSR

```bash
# Quick check via API
curl http://localhost:8000/api/v1/metrics/gsr/current | python -m json.tool
```

---

## 🛑 Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (CAUTION!)
docker-compose down -v
```

---

## 🔧 Troubleshooting

### "Connection refused" errors

**Problem**: Backend not responding

**Solution**:
```bash
# Check if backend is running
docker-compose ps backend

# If not running, check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### "No GSR data" on frontend

**Problem**: Database is empty

**Solution**:
```bash
# You probably skipped step 5 or 6
# Run the data backfill and metric computation steps again
```

### "API key invalid" errors

**Problem**: Wrong API keys in .env

**Solution**:
```bash
# Edit .env file again
nano backend/.env

# Fix the API keys
# Restart services
docker-compose restart backend worker
```

### Frontend shows old data

**Problem**: Browser cache

**Solution**:
```bash
# Hard refresh browser
# Windows/Linux: Ctrl + Shift + R
# Mac: Cmd + Shift + R
```

### Docker errors

**Problem**: Docker not running

**Solution**:
```bash
# Make sure Docker Desktop is running

# On Mac/Windows: Start Docker Desktop app
# On Linux: sudo systemctl start docker
```

---

## 📚 Next Steps

Once everything is working:

1. **Explore the Dashboard**
   - Check current GSR levels
   - Review active signals
   - Monitor gold and silver prices

2. **Try the API**
   - Go to http://localhost:8000/api/docs
   - Test different endpoints
   - View metrics and signals

3. **Configure Alerts** (Optional)
   - Edit backend/.env
   - Set ALERT_EMAIL_ENABLED=true
   - Add your email settings
   - Restart: `docker-compose restart backend`

4. **Run Backtests**
   - Use the API docs
   - POST to /api/v1/backtest/run
   - Experiment with parameters

5. **Chat with AI Advisor** (if AI key configured)
   - POST to /api/v1/ai/chat
   - Ask: "What's the current GSR situation?"
   - Get AI-powered analysis

---

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Read README.md** for detailed documentation
3. **Read DEPLOYMENT.md** for troubleshooting
4. **Check GitHub Issues**

---

## ⚡ Pro Tips

### Faster Startup

```bash
# Only fetch 1 year instead of 5
# Change years=5 to years=1 in step 5
```

### View Data in Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U gsr_user -d gsr_analytics

# Run SQL queries
SELECT COUNT(*) FROM prices;
SELECT * FROM derived_metrics;

# Exit: \q
```

### Monitor Resources

```bash
# See CPU/RAM usage
docker stats
```

### Update Code

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

**You're all set! 🎉**

The system is now running and will automatically update daily. Check back at http://localhost:3000 to see your GSR dashboard!
