"""Prices API endpoints - query historical price data."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Price, Asset
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class PriceResponse(BaseModel):
    id: int
    asset_id: int
    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[float] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PriceResponse])
async def get_prices(
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=1000, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """Get price data for a specific symbol with optional date filtering."""
    # Get asset by symbol
    asset_result = await db.execute(select(Asset).where(Asset.symbol == symbol))
    asset = asset_result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    # Build query
    query = select(Price).where(Price.asset_id == asset.id)

    if start_date:
        query = query.where(Price.timestamp >= start_date)
    if end_date:
        query = query.where(Price.timestamp <= end_date)

    query = query.order_by(Price.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    prices = result.scalars().all()
    return prices


@router.get("/latest/{symbol}", response_model=PriceResponse)
async def get_latest_price(symbol: str, db: AsyncSession = Depends(get_db)):
    """Get the most recent price for a symbol."""
    # Get asset by symbol
    asset_result = await db.execute(select(Asset).where(Asset.symbol == symbol))
    asset = asset_result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    # Get latest price
    query = (
        select(Price)
        .where(Price.asset_id == asset.id)
        .order_by(Price.timestamp.desc())
        .limit(1)
    )

    result = await db.execute(query)
    price = result.scalar_one_or_none()

    if not price:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol}")

    return price
