# Gold-Silver Ratio Analytics & AI Advisor

A comprehensive full-stack analytics platform for tracking, analyzing, and trading the Gold-Silver Ratio (GSR) with AI-powered insights.

## 🎯 Features

### Core Analytics
- **Gold-Silver Ratio Tracking**: Real-time GSR computation with historical data
- **Macro Correlation Analysis**: 90/180-day rolling correlations vs DXY, yields, CPI, oil, equities
- **Regime Classification**: Automatic detection of macro regimes (risk-off, reflation, tightening, etc.)
- **Statistical Signals**: Z-scores, percentile ranks, mean reversion bands

### Trading Tools
- **Signal Generation**: Rule-based GSR swap signals with position sizing
- **Backtesting Engine**: Historical simulation of GSR trading strategies
- **Alert System**: Configurable threshold and composite alerts
- **Performance Tracking**: Win rate, Sharpe ratio, gold ounce accumulation metrics

### AI Advisor
- **Multi-Provider LLM**: OpenAI, Anthropic (Claude), Google (Gemini) support
- **Contextual Analysis**: AI analyzes current GSR, regimes, and market conditions
- **Tool Integration**: AI can query metrics, signals, backtests, and correlations
- **Memory System**: CLAUDE.md-style persistent memory for strategy tracking

### Data Sources
- **Precious Metals**: Metals-API, Alpha Vantage, yfinance
- **Macro Data**: Federal Reserve (FRED) - yields, inflation, unemployment, Fed funds
- **Market Data**: S&P 500, VIX, DXY (dollar index), commodities
- **Sentiment**: CFTC Commitment of Traders (COT) reports

## 🏗️ Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Frontend      │──────│   Backend API   │──────│   PostgreSQL    │
│   (Next.js)     │      │   (FastAPI)     │      │  + TimescaleDB  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                     ┌──────────┼──────────┐
                     │          │          │
              ┌──────┴─────┐  ┌─┴────┐  ┌─┴─────┐
              │   Worker   │  │Redis │  │  AI   │
              │  (Celery)  │  │      │  │ LLMs  │
              └────────────┘  └──────┘  └───────┘
```

### Tech Stack

**Backend:**
- Python 3.11+ with FastAPI
- PostgreSQL 15 with TimescaleDB extension
- SQLAlchemy (async) + Alembic migrations
- APScheduler for data ingestion jobs
- Pandas/NumPy for metric computation

**Frontend:**
- Next.js 14 (App Router)
- React 18 with TypeScript
- TailwindCSS for styling
- TanStack Query for data fetching
- Recharts for visualizations

**AI Integration:**
- OpenAI API (GPT-4)
- Anthropic API (Claude 3)
- Google Generative AI (Gemini)
- Multi-provider abstraction layer

**Infrastructure:**
- Docker + Docker Compose
- Nginx reverse proxy
- Redis for caching

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- API Keys:
  - FRED API key (free at https://fred.stlouisfed.org/docs/api/api_key.html)
  - At least one metals API (Metals-API or Alpha Vantage)
  - At least one AI provider (OpenAI, Anthropic, or Google)

### 1. Clone & Configure

```bash
git clone <repository-url>
cd gold-silver-ratio

# Copy environment template
cp backend/.env.example backend/.env

# Edit .env with your API keys
nano backend/.env
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial assets
docker-compose exec backend python -m app.scripts.seed_data

# Run initial data backfill (fetches 5 years of history)
docker-compose exec backend python -m app.scripts.backfill
```

### 4. Access the Application

Open http://localhost:3000 in your browser.

## 📊 Dashboard Pages

### 1. Home/Overview
- Current GSR with percentile indicator
- Latest signals summary
- Macro snapshot
- AI advisor quick insights

### 2. GSR Dashboard
- Interactive time-series charts
- Gold/silver prices + GSR
- Mean/std bands with zones
- Historical annotations

### 3. Macro & Correlations
- Correlation heatmap (GSR vs 15+ variables)
- Rolling window analysis (30/90/180 days)
- Scatter plots and trend lines
- Regime timeline visualization

### 4. Signals & Strategies
- Active trading signals with strength
- Strategy backtesting interface
- Performance metrics & charts
- Parameter optimization

### 5. AI Advisor
- Chat interface with model selection
- Multi-provider comparison mode
- Context-aware analysis
- Export/share conversations

### 6. Alerts & Calendar
- Alert configuration builder
- Macro event calendar
- Historical alert performance

### 7. Settings
- API key management
- Data provider configuration
- Feature toggles
- Alert preferences

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Code formatting
black app/
isort app/
flake8 app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Type checking
npm run type-check

# Lint
npm run lint

# Build for production
npm run build
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📦 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Config, database, security
│   │   ├── db/           # SQLAlchemy models
│   │   ├── services/     # Business logic
│   │   ├── ingestion/    # Data fetching pipeline
│   │   ├── ai/           # Multi-provider LLM integration
│   │   └── main.py       # FastAPI app
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js pages (App Router)
│   │   ├── components/   # React components
│   │   ├── lib/          # API client, utilities
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── infra/
│   ├── nginx/            # Nginx configuration
│   ├── postgres/         # PostgreSQL init scripts
│   └── docker-compose.yml
│
├── prompts/              # AI prompt templates
│   └── gsr_advisor/
│       ├── system.md
│       └── templates/
│
├── memory/               # CLAUDE.md-style memory files
│   ├── gsr_strategy/
│   └── macro_regime/
│
└── docs/                 # Documentation
    ├── API.md
    ├── DEPLOYMENT.md
    └── DECISIONS.md
```

## 🔑 Environment Variables

See `backend/.env.example` for full list. Key variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/gsr_analytics

# Data Providers
FRED_API_KEY=your_fred_key
ALPHA_VANTAGE_API_KEY=your_av_key
METALS_API_KEY=your_metals_key

# AI Providers (at least one required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## 📈 Data Ingestion Schedule

Data is automatically fetched daily at:
- **20:00 UTC**: Metals prices, ETF data, macro indicators
- **20:05 UTC**: Metric computation (GSR, correlations, stats)
- **20:10 UTC**: Signal generation
- **Every hour**: Alert checking

Manual ingestion:
```bash
docker-compose exec backend python -m app.ingestion.coordinator
```

## 🤖 AI Advisor Usage

The AI advisor has access to these tools:
- `get_latest_metrics`: Current GSR, z-scores, percentiles
- `get_historical_series`: Time series data for backtesting analysis
- `get_current_signals`: Active trading signals
- `get_correlation_data`: GSR correlations with macro variables
- `get_regime_info`: Current and historical regime classifications
- `get_backtest_results`: Strategy performance metrics

Example prompts:
- "What's the current GSR situation and should I consider swapping?"
- "Analyze the correlation between GSR and real yields over the past 90 days"
- "Compare the current regime to the 2020 crisis period"

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- [Deployment Guide](docs/DEPLOYMENT.md) - AWS, VM deployment instructions
- [Architecture Decisions](docs/DECISIONS.md) - Tech choices and rationale
- [Contributing Guide](docs/CONTRIBUTING.md) - Development workflow

## 🛠️ Troubleshooting

**Database connection errors:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Data ingestion failures:**
```bash
# Check API keys are configured
docker-compose exec backend python -c "from app.core.config import settings; print(settings.fred_api_key)"

# Run manual ingestion with verbose logging
docker-compose exec backend python -m app.ingestion.coordinator --verbose
```

**AI provider errors:**
```bash
# Test each provider
docker-compose exec backend python -m app.scripts.test_ai_providers
```

## 📄 License


## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

## 📧 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: [your-email]

---

**Disclaimer**: This software is for educational and research purposes only. It does not provide investment advice. Always do your own research and consult with financial professionals before making investment decisions.
