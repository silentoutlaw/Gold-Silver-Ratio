"""Signals API endpoints - trading signals and recommendations."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db


router = APIRouter()


# Pydantic schemas
class SignalResponse(BaseModel):
    timestamp: datetime
    signal_type: str  # "swap_gold_to_silver" or "swap_silver_to_gold"
    strength: float  # 0-100
    gsr_value: float
    gsr_percentile: float
    gsr_z_score: float
    macro_regime: str
    recommendation: str
    position_size: float  # % of portfolio
    reasoning: str


class SignalHistoryResponse(BaseModel):
    signal: SignalResponse
    outcome: Optional[dict] = None  # Result if historical signal


@router.get("/current", response_model=List[SignalResponse])
async def get_current_signals(db: AsyncSession = Depends(get_db)):
    """Get current active signals based on latest data."""
    # This will be implemented by the signal generation service
    return [
        {
            "timestamp": datetime.utcnow(),
            "signal_type": "swap_gold_to_silver",
            "strength": 75.5,
            "gsr_value": 88.2,
            "gsr_percentile": 95.3,
            "gsr_z_score": 2.5,
            "macro_regime": "tightening_strong_usd",
            "recommendation": "Consider rotating 10-15% of gold holdings to silver",
            "position_size": 12.5,
            "reasoning": "GSR at historical high (95th percentile), USD strength may reverse",
        }
    ]


@router.get("/history", response_model=List[SignalHistoryResponse])
async def get_signal_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get historical signals with outcomes."""
    # This will be implemented by the signal generation service
    return []


@router.get("/performance")
async def get_signal_performance(db: AsyncSession = Depends(get_db)):
    """Get aggregate performance metrics for signal strategy."""
    return {
        "total_signals": 45,
        "win_rate": 0.67,
        "average_hold_days": 120,
        "gold_ounces_gained": 2.5,
        "sharpe_ratio": 1.2,
        "max_drawdown": -0.15,
    }
