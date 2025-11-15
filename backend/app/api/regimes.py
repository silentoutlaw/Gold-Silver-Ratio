"""Regimes API endpoints - macro regime classifications."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Regime, RegimeType
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class RegimeResponse(BaseModel):
    id: int
    label: str
    regime_type: RegimeType
    start_date: datetime
    end_date: Optional[datetime] = None
    methodology_version: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[RegimeResponse])
async def list_regimes(
    regime_type: Optional[RegimeType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List macro regimes with optional filtering."""
    query = select(Regime)

    if regime_type:
        query = query.where(Regime.regime_type == regime_type)
    if start_date:
        query = query.where(Regime.start_date >= start_date)
    if end_date:
        query = query.where(Regime.end_date <= end_date)

    query = query.order_by(Regime.start_date.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    regimes = result.scalars().all()
    return regimes


@router.get("/current", response_model=RegimeResponse)
async def get_current_regime(db: AsyncSession = Depends(get_db)):
    """Get the current active regime."""
    query = (
        select(Regime)
        .where(Regime.end_date.is_(None))
        .order_by(Regime.start_date.desc())
        .limit(1)
    )

    result = await db.execute(query)
    regime = result.scalar_one_or_none()

    if not regime:
        raise HTTPException(status_code=404, detail="No active regime found")

    return regime


@router.get("/{regime_id}", response_model=RegimeResponse)
async def get_regime(regime_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific regime by ID."""
    result = await db.execute(select(Regime).where(Regime.id == regime_id))
    regime = result.scalar_one_or_none()

    if not regime:
        raise HTTPException(status_code=404, detail="Regime not found")

    return regime
