"""Metrics API endpoints - derived metrics like GSR, correlations, z-scores."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import DerivedMetric, MetricValue, Asset, Price
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class MetricResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    computation_method: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class MetricValueResponse(BaseModel):
    id: int
    metric_id: int
    timestamp: datetime
    value: float
    computation_notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MetricResponse])
async def list_metrics(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all available derived metrics."""
    query = select(DerivedMetric).offset(skip).limit(limit)
    result = await db.execute(query)
    metrics = result.scalars().all()
    return metrics


@router.get("/{metric_name}/values", response_model=List[MetricValueResponse])
async def get_metric_values(
    metric_name: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=1000, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """Get time series values for a specific metric."""
    # Get metric by name
    metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == metric_name)
    )
    metric = metric_result.scalar_one_or_none()

    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")

    # Build query
    query = select(MetricValue).where(MetricValue.metric_id == metric.id)

    if start_date:
        query = query.where(MetricValue.timestamp >= start_date)
    if end_date:
        query = query.where(MetricValue.timestamp <= end_date)

    query = query.order_by(MetricValue.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    values = result.scalars().all()
    return values


@router.get("/{metric_name}/latest", response_model=MetricValueResponse)
async def get_latest_metric_value(metric_name: str, db: AsyncSession = Depends(get_db)):
    """Get the most recent value for a metric."""
    # Get metric by name
    metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == metric_name)
    )
    metric = metric_result.scalar_one_or_none()

    if not metric:
        raise HTTPException(status_code=404, detail=f"Metric {metric_name} not found")

    # Get latest value
    query = (
        select(MetricValue)
        .where(MetricValue.metric_id == metric.id)
        .order_by(MetricValue.timestamp.desc())
        .limit(1)
    )

    result = await db.execute(query)
    value = result.scalar_one_or_none()

    if not value:
        raise HTTPException(status_code=404, detail=f"No values for metric {metric_name}")

    return value


@router.get("/gsr/current")
async def get_current_gsr(db: AsyncSession = Depends(get_db)):
    """Get current GSR with percentile and z-score information."""
    # Get GSR metric
    metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    metric = metric_result.scalar_one_or_none()

    if not metric:
        raise HTTPException(status_code=404, detail="GSR metric not found")

    # Get latest GSR value
    value_result = await db.execute(
        select(MetricValue)
        .where(MetricValue.metric_id == metric.id)
        .order_by(MetricValue.timestamp.desc())
        .limit(1)
    )
    value = value_result.scalar_one_or_none()

    if not value:
        raise HTTPException(status_code=404, detail="No GSR data available")

    # Get gold price
    gold_asset_result = await db.execute(
        select(Asset).where(Asset.symbol == "XAU")
    )
    gold_asset = gold_asset_result.scalar_one_or_none()

    gold_price = None
    if gold_asset:
        gold_price_result = await db.execute(
            select(Price)
            .where(Price.asset_id == gold_asset.id)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        gold_price_row = gold_price_result.scalar_one_or_none()
        if gold_price_row:
            gold_price = gold_price_row.close

    # Get silver price
    silver_asset_result = await db.execute(
        select(Asset).where(Asset.symbol == "XAG")
    )
    silver_asset = silver_asset_result.scalar_one_or_none()

    silver_price = None
    if silver_asset:
        silver_price_result = await db.execute(
            select(Price)
            .where(Price.asset_id == silver_asset.id)
            .order_by(Price.timestamp.desc())
            .limit(1)
        )
        silver_price_row = silver_price_result.scalar_one_or_none()
        if silver_price_row:
            silver_price = silver_price_row.close

    # TODO: Calculate percentile and z-score from historical data
    # For now, returning basic GSR value with gold/silver prices
    return {
        "gsr": round(value.value, 2),
        "percentile": None,  # TODO: Calculate from historical data
        "z_score": None,  # TODO: Calculate from historical data
        "mean": None,  # TODO: Calculate from historical data
        "std": None,  # TODO: Calculate from historical data
        "gold_price": round(gold_price, 2) if gold_price else None,
        "silver_price": round(silver_price, 2) if silver_price else None,
        "timestamp": value.timestamp,
    }
