"""
Configuration management API endpoints
Allows users to configure API keys, data sources, and trigger manual operations via UI
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
from pathlib import Path
import asyncio

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class APIKeyConfig(BaseModel):
    fred_api_key: Optional[str] = None
    metals_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None

class DataSourceConfig(BaseModel):
    source_type: str  # "api" or "scraper"
    enabled_sources: List[str]  # ["fred", "metals", "yahoo", "cftc"]

class ManualIngestRequest(BaseModel):
    days_back: int = 7
    sources: Optional[List[str]] = None  # If None, ingest all sources

@router.get("/api-keys")
async def get_api_keys():
    """Get current API key configuration (masked for security)"""
    from app.core.config import settings

    return {
        "fred_api_key": "***" + settings.fred_api_key[-4:] if settings.fred_api_key else None,
        "metals_api_key": "***" + settings.metals_api_key[-4:] if settings.metals_api_key else None,
        "alpha_vantage_api_key": "***" + settings.alpha_vantage_api_key[-4:] if settings.alpha_vantage_api_key else None,
        "openai_api_key": "***" + settings.openai_api_key[-4:] if settings.openai_api_key else None,
        "anthropic_api_key": "***" + settings.anthropic_api_key[-4:] if settings.anthropic_api_key else None,
        "google_ai_api_key": "***" + settings.google_ai_api_key[-4:] if settings.google_ai_api_key else None,
    }

@router.post("/api-keys")
async def update_api_keys(config: APIKeyConfig):
    """Update API keys in environment configuration"""
    try:
        env_path = Path(__file__).parent.parent.parent / ".env"

        # Read existing .env file
        env_vars = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()

        # Update with new keys (only if provided)
        if config.fred_api_key:
            env_vars['FRED_API_KEY'] = config.fred_api_key
        if config.metals_api_key:
            env_vars['METALS_API_KEY'] = config.metals_api_key
        if config.alpha_vantage_api_key:
            env_vars['ALPHA_VANTAGE_API_KEY'] = config.alpha_vantage_api_key
        if config.openai_api_key:
            env_vars['OPENAI_API_KEY'] = config.openai_api_key
        if config.anthropic_api_key:
            env_vars['ANTHROPIC_API_KEY'] = config.anthropic_api_key
        if config.google_ai_api_key:
            env_vars['GOOGLE_AI_API_KEY'] = config.google_ai_api_key

        # Write back to .env file
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        # Update environment variables for current process
        for key, value in env_vars.items():
            os.environ[key] = value

        return {
            "status": "success",
            "message": "API keys updated successfully. Please restart backend for full effect.",
            "keys_updated": [
                k for k in ['fred_api_key', 'metals_api_key', 'alpha_vantage_api_key',
                           'openai_api_key', 'anthropic_api_key', 'google_ai_api_key']
                if getattr(config, k) is not None
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")

@router.post("/ingest-data")
async def trigger_manual_ingest(request: ManualIngestRequest, db: AsyncSession = Depends(get_db)):
    """Manually trigger data ingestion"""
    try:
        from app.ingestion.coordinator import ingest_all_data

        # Run ingestion in background
        result = await ingest_all_data(days_back=request.days_back)

        return {
            "status": "success",
            "message": f"Data ingestion completed for last {request.days_back} days",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")

@router.post("/compute-metrics")
async def trigger_metric_computation():
    """Manually trigger metric computation"""
    try:
        from app.services.metrics import compute_all_metrics

        result = await compute_all_metrics()

        return {
            "status": "success",
            "message": "Metrics computed successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metric computation failed: {str(e)}")

@router.get("/data-sources")
async def get_data_sources():
    """Get available data sources and their status"""
    return {
        "available_sources": [
            {
                "id": "fred",
                "name": "FRED",
                "description": "Federal Reserve Economic Data",
                "type": "api",
                "requires_key": True,
                "data_types": ["macro", "economic_indicators"]
            },
            {
                "id": "metals",
                "name": "Metals-API",
                "description": "Precious metals spot prices",
                "type": "api",
                "requires_key": True,
                "data_types": ["gold", "silver", "platinum", "palladium"]
            },
            {
                "id": "yahoo",
                "name": "Yahoo Finance",
                "description": "ETF and stock market data",
                "type": "scraper",
                "requires_key": False,
                "data_types": ["etf", "indices"]
            },
            {
                "id": "cftc",
                "name": "CFTC",
                "description": "Commitments of Traders reports",
                "type": "scraper",
                "requires_key": False,
                "data_types": ["cot", "positioning"]
            }
        ]
    }

@router.get("/ingestion-status")
async def get_ingestion_status(db: AsyncSession = Depends(get_db)):
    """Get status of last data ingestion"""
    try:
        from app.db.models import Price, MacroValue
        from sqlalchemy import select, func

        # Get counts
        price_count = await db.execute(select(func.count(Price.id)))
        macro_count = await db.execute(select(func.count(MacroValue.id)))

        # Get latest timestamp
        latest_price = await db.execute(
            select(func.max(Price.timestamp))
        )

        return {
            "total_price_records": price_count.scalar(),
            "total_macro_records": macro_count.scalar(),
            "latest_data_timestamp": latest_price.scalar(),
            "status": "ready" if price_count.scalar() > 0 else "no_data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion status: {str(e)}")
