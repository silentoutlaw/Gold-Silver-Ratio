"""Assets API endpoints - manage metals, FX, rates, indices, and commodities."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Asset, AssetType
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class AssetCreate(BaseModel):
    symbol: str
    name: str
    type: AssetType
    source: Optional[str] = None
    metadata: Optional[dict] = None


class AssetResponse(BaseModel):
    id: int
    symbol: str
    name: str
    type: AssetType
    source: Optional[str] = None
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[AssetType] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all assets with optional filtering by type."""
    query = select(Asset)
    if asset_type:
        query = query.where(Asset.type == asset_type)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    assets = result.scalars().all()
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific asset by ID."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.post("/", response_model=AssetResponse, status_code=201)
async def create_asset(asset: AssetCreate, db: AsyncSession = Depends(get_db)):
    """Create a new asset."""
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)
    return db_asset


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an asset."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await db.delete(asset)
    await db.commit()
