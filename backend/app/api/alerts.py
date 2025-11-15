"""Alerts API endpoints - configure and manage user alerts."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.db.models import Alert, AlertType, AlertStatus
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class AlertCreate(BaseModel):
    type: AlertType
    payload: dict  # Alert-specific configuration


class AlertResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    type: AlertType
    status: AlertStatus
    payload: dict
    created_at: datetime
    triggered_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    status: Optional[AlertStatus] = None,
    alert_type: Optional[AlertType] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List alerts with optional filtering."""
    query = select(Alert)

    if status:
        query = query.where(Alert.status == status)
    if alert_type:
        query = query.where(Alert.type == alert_type)

    query = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific alert by ID."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db)):
    """Create a new alert."""
    alert = Alert(
        type=alert_data.type,
        status=AlertStatus.ACTIVE,
        payload=alert_data.payload,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


@router.patch("/{alert_id}/dismiss", response_model=AlertResponse)
async def dismiss_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Dismiss an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.DISMISSED
    alert.dismissed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an alert."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.delete(alert)
    await db.commit()
