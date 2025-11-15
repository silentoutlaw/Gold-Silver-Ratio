# CLAUDE.md - GSR Analytics Project Context

> **Project**: Gold-Silver Ratio Analytics & AI Advisor
> **Status**: Production-Ready v1.1.0 - Deployed & Tested
> **Last Updated**: 2025-11-15 (10:35 UTC)
> **Version**: 1.1.0 - Full User Configuration, Advanced Charts
> **Test Server**: 192.168.99.124 (user: silentoutlaw, password: hyRule-penneewarp)
> **Deployment**: Docker Compose, All Services Running
> **Frontend**: http://192.168.99.124:3000
> **Backend API**: http://192.168.99.124:8000

---

## What This File Is

This file helps AI assistants (and developers) quickly understand the GSR Analytics project. It contains essential context, architecture decisions, and development workflows.

**When to read this**:
- Starting work on the project
- After being away from the codebase
- Before making architectural changes
- When debugging complex issues

---

## Project Overview

### Purpose
A comprehensive analytics platform for tracking and trading the **Gold-Silver Ratio (GSR)** with AI-powered insights. Helps users accumulate more ounces of gold over time by strategically swapping between gold and silver when the ratio reaches statistical extremes.

### Core Strategy
- **High GSR** (e.g., 85-100+): Silver is cheap relative to gold → Consider swapping gold → silver
- **Low GSR** (e.g., 50-65): Silver is expensive relative to gold → Consider swapping silver → gold
- **Goal**: End up with more gold ounces (not USD value) by exploiting mean reversion

### Key Principles
1. **Data-driven** - Everything based on historical statistics and correlations
2. **Risk-aware** - Emphasize uncertainty, position sizing, transaction costs
3. **Transparent** - Show reasoning, calculations, and assumptions
4. **User-Configurable** - All settings managed through web UI, no file editing required

---

## Recent Enhancements (v1.1.0 - 2025-11-15)

### 🎯 User-Friendly Web Configuration
**All configuration now done through the web interface - NO file editing required!**

**New Backend API Endpoints** (`/api/v1/config`)
- `POST /api-keys` - Save API keys directly to backend .env file
- `GET /api-keys` - View current API key status (masked for security)
- `POST /ingest-data` - Manually trigger data refresh from UI
- `POST /compute-metrics` - Manually compute metrics from UI
- `GET /data-sources` - List available data sources (API vs scraper)
- `GET /ingestion-status` - Check current data status

**Enhanced Settings Page**
- ✅ Save API keys directly to backend server (no localStorage)
- ✅ "Refresh Data Now" button - trigger manual data ingestion
- ✅ Real-time status feedback
- ✅ Secure storage (keys encrypted, never exposed)
- ✅ Links to get API keys for all 6 services

**Enhanced Home Page**
- ✅ Quick access buttons to all features (Analytics, Backtest, AI, Settings)
- ✅ Manual refresh button with loading state
- ✅ Direct "Ask AI Advisor" button
- ✅ Improved mobile responsive design
- ✅ Better error handling with actionable guidance
- ✅ Hover animations on action cards

**Improved User Experience**
- No command line required for configuration
- Clear error messages with next steps
- Visual loading states for all async operations
- Mobile-friendly responsive design
- Secure API key management

### 📊 Data Source Flexibility
- Support for both API-based and web scraping data sources
- Yahoo Finance: Public data (no API key required)
- CFTC: Public data (no API key required)
- FRED, Metals-API, Alpha Vantage: API keys required
- User can choose which sources to enable
- Data sources selector visible in Settings page with toggle switches
- Visual distinction between API sources (blue badge) and Scraper sources (green badge)

### 📈 Advanced Interactive Charts
**New AdvancedCharts Component** (`frontend/src/components/AdvancedCharts.tsx`)
- ✅ Multiple chart types: Line, Area, Bar, Candlestick
- ✅ Date range selector with 8 presets:
  - 1 Day, 1 Week, 1 Month, 3 Months
  - 6 Months, 1 Year, All Time, Custom Range
- ✅ Custom date range picker (start/end date inputs)
- ✅ Client-side data filtering based on selected range
- ✅ Responsive design for mobile and desktop
- ✅ Data point counter showing number of values displayed

**Enhanced Analytics Page** (`frontend/src/app/analytics/page.tsx`)
- ✅ GSR history with advanced chart controls
- ✅ Gold price chart with multiple views
- ✅ Silver price chart with multiple views
- ✅ Key insights panel with strategic recommendations
- ✅ Decision framework based on current GSR levels
- ✅ Hover tooltips showing exact values

---

## Architecture Overview

### Tech Stack

**Backend (Python)**
- FastAPI for async REST API
- PostgreSQL 15 + TimescaleDB for time-series data
- SQLAlchemy (async) for ORM
- Alembic for migrations
- Pandas/NumPy for analytics
- APScheduler for cron-like scheduling

**Frontend (TypeScript)**
- Next.js 14 with App Router
- React 18 + TypeScript
- Tailwind CSS for styling
- TanStack Query for data fetching
- Axios for HTTP client

**Infrastructure**
- Docker + Docker Compose
- Nginx reverse proxy
- Redis for caching
- Prometheus/Grafana (optional monitoring)

### System Architecture

```
Data Sources → Ingestion → Storage → Computation → API → Frontend
    ↓            ↓           ↓           ↓         ↓       ↓
  FRED        Coordinator  PostgreSQL  Metrics  FastAPI  Next.js
  Metals-API  Scheduler   TimescaleDB  Signals  Routes   Pages
  Yahoo       Sources     11 Tables    Backtest Tools    UI
  CFTC                                 Alerts
```

### Test Server Information

**Production Deployment**
- **Server IP**: 192.168.99.124
- **SSH User**: silentoutlaw
- **Deploy Path**: /home/silentoutlaw/gsr-analytics
- **Frontend URL**: http://192.168.99.124:3000
- **Backend API**: http://192.168.99.124:8000
- **API Docs**: http://192.168.99.124:8000/api/docs

**Services Running**
- Backend (FastAPI): Port 8000
- Frontend (Next.js): Port 3000
- PostgreSQL + TimescaleDB: Port 5432
- Redis: Port 6379

### Directory Structure

```
backend/
├── app/
│   ├── api/          # API route handlers (9 routers - added config.py)
│   ├── core/         # Config, database, security
│   ├── db/           # SQLAlchemy models (11 tables)
│   ├── services/     # Business logic
│   │   ├── metrics.py    # GSR, correlations, z-scores
│   │   ├── signals.py    # Trading signal generation
│   │   ├── backtest.py   # Strategy backtesting
│   │   └── alerts.py     # Alert checking & delivery
│   ├── ingestion/    # Data pipeline
│   │   ├── coordinator.py    # Orchestrates all sources
│   │   ├── scheduler.py      # APScheduler jobs
│   │   └── sources/          # Data source implementations
│   │       ├── fred.py       # FRED macro data
│   │       ├── metals.py     # Metals prices
│   │       ├── yahoo.py      # ETFs and indices
│   │       └── cftc.py       # COT reports
│   └── ai/           # Multi-provider LLM
│       ├── base.py       # Abstract LLMProvider
│       ├── providers.py  # OpenAI, Anthropic, Google
│       └── tools.py      # AI tool definitions
├── alembic/          # Database migrations
├── tests/            # Pytest test suite
└── requirements.txt

frontend/
├── src/
│   ├── app/          # Next.js pages (App Router)
│   │   ├── layout.tsx
│   │   ├── page.tsx      # Home dashboard
│   │   └── globals.css
│   └── lib/
│       └── api.ts        # API client library
├── package.json
└── tsconfig.json

prompts/              # AI prompt templates
└── gsr_advisor/
    ├── system.md     # Main system prompt (2000+ words)
    └── templates/    # Reusable prompt templates

memory/               # CLAUDE.md-style memory
├── gsr_strategy/     # User strategy & goals
└── macro_regime/     # Regime library & patterns

docs/
├── README.md         # Main documentation
├── DECISIONS.md      # Architecture Decision Records
├── DEPLOYMENT.md     # Deployment guides
└── QUICKSTART.md     # 5-minute setup
```

---

## Database Schema

### Core Tables (11 total)

**Assets & Prices** (Time-series)
- `assets` - Metals, FX, indices, ETFs (symbol, name, type)
- `prices` - OHLCV price data (hypertable for time-series optimization)

**Macro Data**
- `macro_series` - Economic indicators (CPI, yields, unemployment)
- `macro_values` - Time-series values for macro series (hypertable)

**Computed Metrics**
- `derived_metrics` - Metric definitions (GSR, correlations, z-scores)
- `metric_values` - Computed metric values (hypertable)

**Regime & Signals**
- `regimes` - Macro regime classifications (risk-off, reflation, etc.)

**Alerts**
- `alerts` - User alert configurations (threshold, composite, macro event)

**AI System**
- `prompts` - AI prompt templates (versioned)
- `conversations` - AI chat sessions
- `conversation_messages` - Individual messages in conversations

### Important Relationships

```
Asset 1──N Price
MacroSeries 1──N MacroValue
DerivedMetric 1──N MetricValue
Conversation 1──N ConversationMessage
```

### TimescaleDB Hypertables

These tables are optimized for time-series queries:
- `prices` - Partitioned by timestamp
- `macro_values` - Partitioned by date
- `metric_values` - Partitioned by timestamp

---

## Key Workflows

### 1. Data Ingestion (Daily at 20:00 UTC)

```python
# Triggered by APScheduler
coordinator.ingest_all_data()
  ↓
  ├─ FRED: Fetch macro indicators (yields, CPI, unemployment)
  ├─ Metals: Fetch gold, silver, platinum, palladium prices
  ├─ Yahoo: Fetch ETF data (GLD, SLV, GDX, etc.)
  └─ CFTC: Fetch COT reports (speculative positioning)
  ↓
  Store in database (assets, prices, macro_values)
```

### 2. Metric Computation (20:05 UTC)

```python
# Triggered 5 minutes after ingestion
services.metrics.compute_all_metrics()
  ↓
  ├─ Compute GSR (gold_price / silver_price)
  ├─ Compute rolling stats (mean, std, z-score, percentile)
  │  └─ Windows: 30, 90, 180, 365 days
  ├─ Compute correlations (GSR vs DXY, yields, oil, S&P 500, VIX)
  │  └─ Windows: 30, 90, 180 days
  └─ Store in metric_values table
```

### 3. Signal Generation (20:10 UTC)

```python
# Triggered 10 minutes after ingestion
services.signals.generate_signals()
  ↓
  ├─ Get current GSR analysis (value, z-score, percentile)
  ├─ Check thresholds:
  │  ├─ High GSR: >= 85 OR percentile >= 85% → "swap_gold_to_silver"
  │  └─ Low GSR: <= 65 OR percentile <= 20% → "swap_silver_to_gold"
  ├─ Calculate signal strength (0-100)
  ├─ Recommend position size (10-20%)
  └─ Return signals with reasoning
```

### 4. Alert Checking (Every hour)

```python
# Triggered hourly
services.alerts.check_alerts()
  ↓
  ├─ Get all active alerts
  ├─ For each alert:
  │  ├─ Check condition (ratio_band, threshold, composite, macro_event)
  │  ├─ If triggered:
  │  │  ├─ Update alert status
  │  │  └─ Send notifications (email, webhook)
  └─ Log results
```

### 5. Backtesting (On-demand via API)

```python
# POST /api/v1/backtest/run
services.backtest.run_backtest(config)
  ↓
  ├─ Get historical GSR data
  ├─ Simulate trading:
  │  ├─ Start with initial_gold_oz
  │  ├─ When GSR >= high_threshold: swap gold → silver
  │  ├─ When GSR <= low_threshold: swap silver → gold
  │  └─ Apply transaction costs
  ├─ Calculate metrics:
  │  ├─ Final gold oz (in gold-equivalent)
  │  ├─ Total swaps, win rate
  │  ├─ Sharpe ratio, max drawdown
  └─ Return results + equity curve
```

### 6. AI Advisor Query

```python
# POST /api/v1/ai/chat
ai.providers.get_ai_response(message, provider)
  ↓
  ├─ Load system prompt (prompts/gsr_advisor/system.md)
  ├─ Load conversation history
  ├─ Load memory context (memory/gsr_strategy/CLAUDE.md)
  ├─ Send to LLM with tools available:
  │  ├─ get_latest_metrics
  │  ├─ get_historical_series
  │  ├─ get_current_signals
  │  ├─ get_backtest_results
  │  ├─ get_correlation_data
  │  └─ get_regime_info
  ├─ Process response
  ├─ Store in conversation_messages
  └─ Return to user
```

---

## Development Workflows

### Adding a New Metric

1. **Define metric** in `services/metrics.py`:
```python
async def compute_my_metric(db: AsyncSession) -> int:
    # Get or create metric definition
    metric = DerivedMetric(
        name="my_metric",
        description="Description",
        computation_method="How it's calculated"
    )
    db.add(metric)
    await db.flush()

    # Compute values
    for timestamp, value in data:
        metric_value = MetricValue(
            metric_id=metric.id,
            timestamp=timestamp,
            value=value
        )
        db.add(metric_value)

    await db.commit()
    return count
```

2. **Add to compute_all_metrics()** in same file:
```python
async def compute_all_metrics():
    # ... existing metrics ...
    stats["my_metric_computed"] = await compute_my_metric(db)
```

3. **Test manually**:
```bash
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
asyncio.run(compute_all_metrics())
"
```

### Adding a New API Endpoint

1. **Create route** in `api/my_module.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint(db: AsyncSession = Depends(get_db)):
    # Implementation
    return {"result": "data"}
```

2. **Register router** in `main.py`:
```python
from app.api import my_module
app.include_router(my_module.router, prefix="/api/v1/my", tags=["my"])
```

3. **Test via API docs**: http://localhost:8000/api/docs

### Adding a New Data Source

1. **Create source class** in `ingestion/sources/my_source.py`:
```python
from app.ingestion.sources.base import DataSource, PriceData, MacroData

class MySource(DataSource):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)

    def get_source_name(self) -> str:
        return "MySource"

    async def fetch_prices(self, symbols, start_date, end_date):
        # Implementation
        return [PriceData(...), ...]

    async def fetch_macro_data(self, series_codes, start_date, end_date):
        # Implementation
        return [MacroData(...), ...]
```

2. **Add to coordinator** in `ingestion/coordinator.py`:
```python
async def ingest_my_source_data(db, start_date, end_date):
    source = MySource()
    data = await source.fetch_prices(...)
    count = await store_price_data(db, data, AssetType.COMMODITY)
    return count

async def ingest_all_data(days_back=1):
    # ... existing sources ...
    stats["my_source"] = await ingest_my_source_data(db, start_date, end_date)
```

### Running Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add my_table"

# Review generated migration in backend/alembic/versions/

# Apply migration
docker-compose exec backend alembic upgrade head

# Rollback if needed
docker-compose exec backend alembic downgrade -1
```

---

## Important Patterns & Conventions

### 1. Async/Await Everywhere
All database operations and I/O use async/await:
```python
async def my_function(db: AsyncSession):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()
```

### 2. Database Sessions
Always use dependency injection for database sessions:
```python
@router.get("/endpoint")
async def endpoint(db: AsyncSession = Depends(get_db)):
    # db session auto-commits on success, rollback on exception
```

### 3. Error Handling
Wrap risky operations in try/except:
```python
try:
    data = await fetch_from_api()
except Exception as e:
    logger.error(f"Failed to fetch: {e}")
    stats["errors"].append(str(e))
```

### 4. Logging
Use Python logging module:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Starting process")
logger.warning("Something unusual")
logger.error("Something failed", exc_info=True)
```

### 5. Configuration
All config via environment variables in `core/config.py`:
```python
from app.core.config import settings

api_key = settings.fred_api_key
```

### 6. Type Hints
Always use type hints (enforced by mypy):
```python
def calculate_gsr(gold: float, silver: float) -> float:
    return gold / silver

async def get_metrics(db: AsyncSession) -> List[Dict[str, Any]]:
    # ...
```

### 7. Pydantic Models
Use Pydantic for request/response validation:
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    name: str
    value: float

@router.post("/endpoint")
async def endpoint(data: MyRequest):
    # data is validated automatically
```

---

## Common Tasks

### Start Development Environment

```bash
docker-compose up -d
docker-compose logs -f backend
```

### Run Tests

```bash
docker-compose exec backend pytest
docker-compose exec backend pytest -v --cov=app
```

### Access Database

```bash
docker-compose exec postgres psql -U gsr_user -d gsr_analytics

# Useful queries:
\dt                    # List tables
\d prices             # Describe table
SELECT COUNT(*) FROM prices;
SELECT * FROM assets LIMIT 10;
```

### Manual Data Fetch

```bash
# Fetch last 7 days
docker-compose exec backend python -c "
import asyncio
from app.ingestion.coordinator import ingest_all_data
result = asyncio.run(ingest_all_data(days_back=7))
print(result)
"
```

### Check API Health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/metrics/gsr/current
```

### View Logs

```bash
docker-compose logs -f backend    # Backend logs
docker-compose logs -f worker     # Worker logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs --tail=100    # Last 100 lines all services
```

### Restart Services

```bash
docker-compose restart backend
docker-compose restart worker
docker-compose down && docker-compose up -d  # Full restart
```

---

## Known Issues & Gotchas

### 1. API Rate Limits
**Issue**: Free API tiers have rate limits
- FRED: 120 requests/minute
- Alpha Vantage: 25 requests/day (free tier)
- Metals-API: 100 requests/month (free tier)

**Solution**: Built-in rate limiting and delays in data sources. For development, use `days_back=30` instead of `years=5`.

### 2. TimescaleDB Setup
**Issue**: TimescaleDB extension must be enabled manually

**Solution**: After first run:
```sql
docker-compose exec postgres psql -U gsr_user -d gsr_analytics
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
SELECT create_hypertable('prices', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('metric_values', 'timestamp', if_not_exists => TRUE);
```

### 3. CORS Errors in Frontend
**Issue**: Frontend can't connect to backend

**Solution**: Check `backend/.env`:
```bash
CORS_ORIGINS=["http://localhost:3000"]
```

### 4. Empty Metrics
**Issue**: Metrics API returns no data

**Solution**: Run metric computation:
```bash
docker-compose exec backend python -c "
import asyncio
from app.services.metrics import compute_all_metrics
asyncio.run(compute_all_metrics())
"
```

### 5. Docker Volume Permissions
**Issue**: Permission denied errors on Linux

**Solution**: Fix ownership:
```bash
sudo chown -R $USER:$USER .
```

---

## AI Advisor Context

### System Prompt Location
`prompts/gsr_advisor/system.md` - 2,000+ word comprehensive prompt

**Key Instructions for AI:**
- Be precise, transparent, conservative
- Separate facts, conclusions, speculation
- Emphasize risk management and uncertainty
- Never give personalized investment advice
- Never present anything as guaranteed

### Memory Files

**`memory/gsr_strategy/CLAUDE.md`**
- User's strategic goals and preferences
- Key decisions made (thresholds, position sizes)
- Open questions and hypotheses to test
- Backtest results and learnings

**`memory/macro_regime/CLAUDE.md`**
- Historical regime library (COVID, reflation, tightening)
- Correlation patterns by regime
- Regime transition signals
- Decision rules for regime-aware signals

### AI Tools Available

1. **get_latest_metrics** - Current GSR, z-scores, percentiles
2. **get_historical_series** - Time series data for analysis
3. **get_current_signals** - Active trading signals
4. **get_backtest_results** - Strategy performance metrics
5. **get_correlation_data** - GSR correlations with macro variables
6. **get_regime_info** - Current and historical regime classifications

---

## Performance Considerations

### Database Queries
- Use indexes on frequently queried columns (timestamp, asset_id, metric_id)
- Leverage TimescaleDB hypertables for time-series queries
- Use `select()` with specific columns, not `select(*)`
- Batch inserts when possible

### Memory Usage
- Backend: ~500MB idle, ~2GB during data ingestion
- PostgreSQL: ~200MB base, grows with data
- Frontend: ~100MB (Next.js dev server)
- Total: 4GB RAM recommended

### API Response Times
- `/health`: <10ms
- `/metrics/gsr/current`: <100ms (cached)
- `/metrics/{metric}/values`: 100-500ms (depends on date range)
- `/backtest/run`: 2-10s (depends on timeframe)
- `/ai/chat`: 2-30s (depends on AI provider and query complexity)

---

## Testing Strategy

### Unit Tests
Located in `backend/tests/`
```bash
pytest backend/tests/test_metrics.py
pytest backend/tests/ -v
```

### Integration Tests
Test full workflows:
```bash
# Test data ingestion
pytest backend/tests/test_integration.py::test_full_ingestion_cycle

# Test API endpoints
pytest backend/tests/test_api.py
```

### Manual Testing Checklist
- [ ] Start services: `docker-compose up -d`
- [ ] Check health: `curl localhost:8000/health`
- [ ] Fetch data: Run manual ingestion
- [ ] Compute metrics: Run metric computation
- [ ] View frontend: Open http://localhost:3000
- [ ] Test API: Open http://localhost:8000/api/docs
- [ ] Check logs: `docker-compose logs -f`

---

## Security Notes

### API Keys
- **NEVER** commit API keys to Git
- Store in `backend/.env` (gitignored)
- Use environment variables only
- Encrypt sensitive keys in database (see `core/security.py`)

### Database
- Default credentials are for development only
- Change `POSTGRES_PASSWORD` in production
- Use `DATABASE_URL` environment variable
- Enable SSL for production databases

### Frontend
- API calls go through Nginx proxy
- CORS configured in backend
- No sensitive data in client-side code
- Use environment variables for API URL

---

## Deployment Checklist

### Pre-Deployment
- [ ] Set all API keys in `.env`
- [ ] Change database password
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure SSL certificates
- [ ] Update `CORS_ORIGINS` to production domain
- [ ] Enable alerts (email/webhook)

### Post-Deployment
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Backfill historical data
- [ ] Compute initial metrics
- [ ] Test all API endpoints
- [ ] Verify scheduled jobs are running
- [ ] Setup monitoring (Prometheus/Grafana)
- [ ] Configure backups

See `docs/DEPLOYMENT.md` for full guide.

---

## Maintenance

### Daily
- Automated data ingestion runs at configured time
- Check logs for errors: `docker-compose logs --tail=100`

### Weekly
- Review logs for warnings/errors
- Check disk space: `df -h`
- Verify data ingestion success
- Test API endpoints

### Monthly
- Update dependencies (security patches)
- Review and optimize database indexes
- Backup database
- Review alert accuracy

### As Needed
- Add new data sources
- Optimize slow queries
- Adjust signal parameters
- Update AI prompts based on feedback

---

## Helpful Resources

### Documentation
- **README.md** - Project overview and features
- **QUICKSTART.md** - 5-minute setup guide
- **DECISIONS.md** - Architectural decisions (10 ADRs)
- **DEPLOYMENT.md** - VM and AWS deployment guides

### External Resources
- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- TimescaleDB: https://docs.timescale.com/
- Next.js: https://nextjs.org/docs
- FRED API: https://fred.stlouisfed.org/docs/api/

---

## Contact & Support

For issues or questions:
1. Check this CLAUDE.md file
2. Review README.md and DEPLOYMENT.md
3. Check logs: `docker-compose logs -f`
4. Search code for similar patterns
5. Check GitHub Issues (if applicable)

---

## Version History

**v1.1.0** (2025-11-15) ✅ DEPLOYED
- Advanced interactive charts (Line, Area, Bar, Candlestick)
- Date range selector with 8 presets + custom date ranges
- Data source selector with API vs Scraper distinction
- Manual data refresh button (triggers ingestion + metrics)
- Web-based API key configuration (no file editing required)
- Enhanced Settings page with source toggles
- Enhanced Home page with quick access buttons
- All configuration via UI (no terminal needed)
- Real-time status feedback and error handling
- Mobile-responsive design improvements
- Deployed to 192.168.99.124 - All services running

**v1.0.0** (2025-11-14)
- Initial production release
- Complete backend API (8 routers, 50+ endpoints)
- Complete data ingestion (4 sources)
- Multi-provider AI integration
- Frontend dashboard (Home page)
- Full Docker deployment
- Comprehensive documentation

---

## Current Deployment Status (2025-11-15)

### Test Server: 192.168.99.124
- **Frontend**: http://192.168.99.124:3000 ✅ Running
- **Backend API**: http://192.168.99.124:8000 ✅ Running
- **API Docs**: http://192.168.99.124:8000/api/docs
- **PostgreSQL**: 192.168.99.124:5432 ✅ Healthy
- **Redis**: 192.168.99.124:6379 ✅ Healthy

### Key Pages to Test
- **Home**: http://192.168.99.124:3000
  - Dashboard with GSR metrics
  - Quick access buttons to all features
  - Manual refresh button

- **Settings**: http://192.168.99.124:3000/settings
  - Data source selector (API vs Scraper)
  - API key configuration for 6 services
  - "Refresh Data Now" button
  - How It Works guide

- **Analytics**: http://192.168.99.124:3000/analytics
  - GSR history with advanced chart controls
  - Gold price with multiple chart types
  - Silver price with date range selectors
  - Custom date range picker
  - Key insights panel

### To Access Test Server
```bash
ssh silentoutlaw@192.168.99.124
# Password: hyRule-penneewarp
cd /home/silentoutlaw/gsr-analytics
docker compose logs -f  # View all logs
docker compose ps       # Check service status
```

---

**Remember**: This project is for educational purposes only. It does not provide investment advice. Always do your own research and consult with financial professionals before making investment decisions.

---

*This CLAUDE.md file is maintained by the development team. Update it when making significant architectural changes.*
