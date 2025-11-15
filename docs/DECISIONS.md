# Architectural Decisions Record

This document records the key architectural and technical decisions made during the development of the GSR Analytics system.

## Format

Each decision is documented with:
- **Context**: Why did we face this decision?
- **Decision**: What did we choose?
- **Rationale**: Why did we make this choice?
- **Alternatives**: What other options were considered?
- **Consequences**: What are the tradeoffs?

---

## ADR-001: Backend Language and Framework

**Date**: 2025-11-14
**Status**: Accepted

### Context
Needed to choose backend technology stack. Options were TypeScript (NestJS) or Python (FastAPI).

### Decision
**Python 3.11+ with FastAPI**

### Rationale
1. **Data Science Ecosystem**: NumPy, Pandas, SciPy are essential for metric computation (GSR calculations, rolling correlations, statistical analysis)
2. **ML Future-Proofing**: Plan mentioned optional ML for regime classification; Python has superior ML libraries
3. **API Maturity**: FastAPI provides excellent async support, automatic OpenAPI docs, and Pydantic validation
4. **Team Experience**: Python is more accessible for data-focused development

### Alternatives Considered
- **TypeScript + NestJS**: Better for full-stack TypeScript consistency, but weaker data science libraries
- **Go**: Excellent performance but immature data science ecosystem
- **Julia**: Great for numerical computing but smaller ecosystem and community

### Consequences
**Positive:**
- Easy integration with data analysis libraries
- Strong async support via asyncio
- Rich ecosystem for API integrations (FRED, metals APIs, etc.)

**Negative:**
- GIL can be a bottleneck (mitigated by async I/O and worker processes)
- Slightly slower than compiled languages for compute-heavy tasks
- Need to maintain Python version consistency across environments

---

## ADR-002: Database Choice

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need a database that handles both relational data (assets, alerts, conversations) and high-volume time-series data (prices, metrics).

### Decision
**PostgreSQL 15 with TimescaleDB extension**

### Rationale
1. **Time-Series Optimization**: TimescaleDB provides hypertables for efficient time-series queries
2. **Relational Integrity**: ACID compliance for critical data (trades, alerts, user configs)
3. **JSON Support**: Native JSONB for flexible metadata storage
4. **Mature Ecosystem**: Well-supported, extensive tooling, battle-tested
5. **Cost**: Open-source, no licensing fees

### Alternatives Considered
- **InfluxDB**: Pure time-series DB but weak relational support, would need secondary DB
- **MongoDB**: Good for flexibility but weaker time-series queries and no ACID guarantees
- **ClickHouse**: Excellent for analytics but overkill for this scale, harder to operate
- **Plain PostgreSQL**: Works but TimescaleDB adds significant time-series performance

### Consequences
**Positive:**
- Single database for all data types
- Excellent query performance on time-series
- Automatic data retention policies via TimescaleDB
- Easy to scale vertically

**Negative:**
- Requires TimescaleDB extension (adds deployment complexity)
- Vertical scaling limits (can't trivially shard)
- Backup/restore more complex than simple key-value stores

---

## ADR-003: Frontend Framework

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need a modern, performant frontend for complex dashboards with real-time data visualization.

### Decision
**Next.js 14 (App Router) + React 18 + TypeScript**

### Rationale
1. **App Router**: Modern React Server Components for better performance
2. **TypeScript**: Type safety critical for complex data structures (metrics, signals, backtests)
3. **SSR/SSG**: Can pre-render static pages for better initial load times
4. **Developer Experience**: Excellent tooling, hot reload, built-in routing
5. **Ecosystem**: Rich component libraries (TanStack Query, Recharts, etc.)

### Alternatives Considered
- **Vite + React**: Faster builds but requires manual routing setup
- **SvelteKit**: Excellent performance but smaller ecosystem
- **Vue 3 + Nuxt**: Good option but team more familiar with React
- **Vanilla HTML/JS**: Too limited for complex interactive dashboards

### Consequences
**Positive:**
- Type safety reduces bugs in complex data transformations
- Server components improve performance for data-heavy pages
- Large ecosystem for charting and data visualization
- Easy integration with backend API

**Negative:**
- Next.js adds complexity vs. simple React app
- Bundle size can be large (mitigated by code splitting)
- Learning curve for App Router (newer paradigm)

---

## ADR-004: Multi-Provider AI Abstraction

**Date**: 2025-11-14
**Status**: Accepted

### Context
Plan requires support for multiple LLM providers (OpenAI, Anthropic, Google) with ability to switch or compare responses.

### Decision
**Abstract base class (`LLMProvider`) with concrete implementations for each provider**

### Rationale
1. **Provider Independence**: Users can choose based on cost, performance, or preference
2. **Redundancy**: If one provider has outages, can switch to another
3. **Comparison Mode**: Can send same prompt to multiple providers for validation
4. **Future-Proofing**: Easy to add new providers (Mistral, local models, etc.)

### Alternatives Considered
- **LangChain**: Too heavyweight, many unused features, adds dependency complexity
- **OpenAI-only**: Vendor lock-in, no redundancy
- **Raw API calls**: Would need to duplicate logic for each provider

### Consequences
**Positive:**
- Users not locked into single provider
- Can optimize cost by routing simple queries to cheaper models
- Comparison mode helps validate AI outputs

**Negative:**
- More code to maintain (3+ provider implementations)
- Slight overhead in abstraction layer
- Provider-specific features may not map cleanly across all providers

---

## ADR-005: Data Ingestion Architecture

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need to fetch data from 5+ different APIs (FRED, metals, Yahoo Finance, CFTC) on a schedule, with error handling and retries.

### Decision
**Coordinator pattern with pluggable data sources and APScheduler for scheduling**

### Rationale
1. **Separation of Concerns**: Each data source has its own module with specific logic
2. **Testability**: Can test each source independently
3. **Extensibility**: Easy to add new data sources
4. **Scheduling**: APScheduler is lightweight and sufficient for daily jobs
5. **Error Isolation**: One source failing doesn't block others

### Alternatives Considered
- **Celery**: More powerful but overkill for daily batch jobs, requires message broker
- **Airflow**: Enterprise-grade but too complex for this scale
- **Cron + CLI scripts**: Works but harder to monitor and log
- **Monolithic fetcher**: All sources in one module, harder to test and maintain

### Consequences
**Positive:**
- Clear separation of data source logic
- Easy to add/remove sources
- Can run sources in parallel
- Simple monitoring and logging

**Negative:**
- APScheduler keeps state in memory (restarts lose schedule state)
- Not ideal for very high-frequency updates (intraday)
- Manual management of API rate limits per source

---

## ADR-006: Metric Computation Strategy

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need to compute GSR and dozens of derived metrics (rolling stats, correlations, z-scores, percentiles) efficiently.

### Decision
**Batch computation with Pandas/NumPy after data ingestion, store results in metric tables**

### Rationale
1. **Performance**: Pandas vectorized operations are fast for batch time-series computations
2. **Caching**: Precompute and store; don't recalculate on every API request
3. **Consistency**: All API consumers get same metric values
4. **Simplicity**: Pandas rolling windows, correlations, and stats are well-tested

### Alternatives Considered
- **On-demand computation**: Calculate metrics when requested via API (too slow, inconsistent)
- **Stream processing (Kafka, Flink)**: Overkill for daily batch updates
- **Database-native functions**: PostgreSQL window functions work but less flexible than Pandas
- **Incremental updates**: Only compute new days (complex to manage state, error-prone)

### Consequences
**Positive:**
- Fast API responses (metrics pre-computed)
- Consistent metric values across all consumers
- Easy to backfill historical metrics

**Negative:**
- Metrics lag by ingestion cycle (typically daily)
- Requires storage space for all metric values
- Must recompute if methodology changes (backfill cost)

---

## ADR-007: Docker Compose for Development and Deployment

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need a deployment solution that works for local development, single-server VMs, and cloud environments.

### Decision
**Docker Compose with separate services for backend, frontend, database, worker, and nginx**

### Rationale
1. **Simplicity**: Single `docker-compose up` starts entire stack
2. **Portability**: Works on Windows, Mac, Linux, and cloud VMs
3. **Development**: Volumes for hot reload during development
4. **Production-Ready**: Can deploy directly to VMs or use as base for Kubernetes
5. **VM-Agnostic**: Not locked into specific cloud provider

### Alternatives Considered
- **Kubernetes**: Too complex for single-server deployment, overkill for this scale
- **Docker Swarm**: Less popular than K8s, smaller ecosystem
- **Bare metal**: No containerization makes deployment and dependencies harder
- **Serverless (Lambda, Cloud Run)**: Doesn't fit long-running worker and database needs

### Consequences
**Positive:**
- Easy local development (matches production)
- Fast deployment to VMs (single docker-compose file)
- Service isolation (frontend, backend, worker separate)
- Easy to add services (e.g., Prometheus, Grafana)

**Negative:**
- Docker Compose not ideal for multi-server clustering (would need orchestrator)
- Requires Docker knowledge
- Volume management can be tricky

---

## ADR-008: TanStack Query for Frontend Data Fetching

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need efficient client-side data fetching with caching, background updates, and stale-while-revalidate patterns.

### Decision
**TanStack Query (React Query) for all backend API calls**

### Rationale
1. **Caching**: Automatic caching reduces redundant API calls
2. **Background Refresh**: Keeps data fresh without blocking UI
3. **Devtools**: Excellent debugging tools for query state
4. **TypeScript**: Full type safety for API responses
5. **Standard**: De facto standard for React data fetching

### Alternatives Considered
- **SWR**: Similar to TanStack Query but smaller feature set
- **Redux + RTK Query**: More complex, overkill for this use case
- **Plain fetch/axios**: No caching, would need manual state management
- **GraphQL + Apollo**: Adds backend complexity (REST API already defined)

### Consequences
**Positive:**
- Automatic caching and background updates
- Optimistic updates for better UX
- Error and loading state management
- Prefetching for anticipated navigation

**Negative:**
- Learning curve for TanStack Query patterns
- Can over-fetch if not carefully configured
- Cache invalidation strategy requires planning

---

## ADR-009: Rolling Window Sizes for Statistics

**Date**: 2025-11-14
**Status**: Accepted

### Context
Need to choose window sizes for rolling statistics (z-scores, percentiles, correlations).

### Decision
**Primary windows: 30, 90, 180, 365 days**

### Rationale
1. **30-day**: Captures very recent behavior, responsive to regime changes
2. **90-day**: Balances responsiveness and stability (Plan's default)
3. **180-day**: ~6 months, smooths out quarterly noise
4. **365-day**: Full-year view, captures seasonal patterns

### Alternatives Considered
- **Single window (90-day only)**: Too rigid, doesn't capture multi-timeframe view
- **More granular (7, 14, 21 days)**: Too noisy, less stable
- **Longer windows (2-year, 5-year)**: Too slow to react to regime changes

### Consequences
**Positive:**
- Multi-timeframe analysis helps identify regime shifts
- 90-day matches Plan's recommendation
- 30-day catches early signals; 365-day confirms long-term trends

**Negative:**
- More metrics to compute and store (4x per metric)
- UI complexity showing multiple windows
- Potential for conflicting signals across windows

---

## ADR-010: CLAUDE.md Memory File Format

**Date**: 2025-11-14
**Status**: Accepted

### Context
AI advisor needs persistent memory of user's strategy, goals, and past decisions to provide contextual advice.

### Decision
**Markdown files in `memory/` directory, loaded into AI system prompts on each session**

### Rationale
1. **Human-Readable**: User can inspect and edit memory files directly
2. **Version Control**: Git tracks changes to strategy over time
3. **Structured**: Markdown headings provide clear organization
4. **LLM-Friendly**: All major LLMs handle markdown natively
5. **No DB Dependency**: Memory persists even if database is reset

### Alternatives Considered
- **Database table**: More queryable but less transparent to user
- **JSON files**: Machine-readable but harder for humans to edit
- **Vector database (Pinecone, Weaviate)**: Overkill for structured memory
- **No memory**: AI forgets context between sessions (poor UX)

### Consequences
**Positive:**
- User can audit and edit strategy memory
- Version controlled (see how strategy evolved)
- Simple to backup and restore
- No additional infrastructure

**Negative:**
- Manual updates required (or AI needs write access to files)
- Not easily queryable (full-text search only)
- Can grow large over time (need pruning strategy)

---

## Summary of Key Decisions

| Area | Decision | Primary Reason |
|------|----------|----------------|
| Backend | Python + FastAPI | Data science ecosystem (Pandas, NumPy) |
| Database | PostgreSQL + TimescaleDB | Time-series optimization + relational integrity |
| Frontend | Next.js + React + TypeScript | Modern, type-safe, SSR/SSG support |
| AI | Multi-provider abstraction | Flexibility, redundancy, comparison mode |
| Ingestion | Coordinator + APScheduler | Simple, extensible, error isolation |
| Metrics | Batch compute with Pandas | Performance, caching, consistency |
| Deployment | Docker Compose | Simplicity, portability, VM-agnostic |
| Data Fetching | TanStack Query | Caching, background updates, devtools |
| Rolling Windows | 30/90/180/365 days | Multi-timeframe analysis |
| Memory | Markdown files | Human-readable, version-controlled |

---

**Maintained by**: GSR Analytics Team
**Last Updated**: 2025-11-14
