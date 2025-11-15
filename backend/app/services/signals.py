"""
Signal generation service.
Generates GSR-based trading signals with regime context and position sizing.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import AsyncSessionLocal
from app.db.models import DerivedMetric, MetricValue, Regime
from app.services.metrics import get_current_gsr_analysis

logger = logging.getLogger(__name__)


class Signal:
    """Trading signal representation."""

    def __init__(
        self,
        signal_type: str,
        strength: float,
        gsr_value: float,
        gsr_percentile: float,
        gsr_z_score: float,
        macro_regime: str,
        recommendation: str,
        position_size: float,
        reasoning: str,
        timestamp: datetime,
    ):
        self.signal_type = signal_type
        self.strength = strength
        self.gsr_value = gsr_value
        self.gsr_percentile = gsr_percentile
        self.gsr_z_score = gsr_z_score
        self.macro_regime = macro_regime
        self.recommendation = recommendation
        self.position_size = position_size
        self.reasoning = reasoning
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary."""
        return {
            "timestamp": self.timestamp,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "gsr_value": self.gsr_value,
            "gsr_percentile": self.gsr_percentile,
            "gsr_z_score": self.gsr_z_score,
            "macro_regime": self.macro_regime,
            "recommendation": self.recommendation,
            "position_size": self.position_size,
            "reasoning": self.reasoning,
        }


async def generate_signals() -> Dict[str, Any]:
    """
    Generate current trading signals based on GSR and macro conditions.

    Returns:
        Dictionary with signal generation statistics
    """
    logger.info("Starting signal generation")

    stats = {
        "start_time": datetime.now(),
        "signals_generated": 0,
        "errors": [],
    }

    async with AsyncSessionLocal() as db:
        try:
            signals = await generate_current_signals(db)
            stats["signals_generated"] = len(signals)
            stats["signals"] = [s.to_dict() for s in signals]

            stats["end_time"] = datetime.now()
            stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()

            logger.info(f"Signal generation completed: {stats}")

        except Exception as e:
            logger.error(f"Signal generation failed: {e}", exc_info=True)
            stats["errors"].append(str(e))

    return stats


async def generate_current_signals(db: AsyncSession) -> List[Signal]:
    """
    Generate signals based on current GSR levels and macro conditions.

    Args:
        db: Database session

    Returns:
        List of Signal objects
    """
    signals = []

    # Get current GSR analysis
    gsr_analysis = await get_current_gsr_analysis(db)

    if not gsr_analysis:
        logger.warning("No GSR data available for signal generation")
        return signals

    gsr = gsr_analysis["gsr"]
    z_score = gsr_analysis.get("z_score", 0.0)
    percentile = gsr_analysis.get("percentile", 50.0)

    # Get current regime (simplified - would use actual regime detection)
    regime = await get_current_regime(db)
    regime_type = regime.regime_type.value if regime else "unknown"

    # Signal generation logic
    # High GSR signal (swap gold -> silver)
    if gsr >= 85.0 or (percentile is not None and percentile >= 85.0):
        strength = calculate_signal_strength(gsr, z_score, percentile, "high")

        position_size = calculate_position_size(strength, gsr)

        reasoning_parts = []
        if gsr >= 85.0:
            reasoning_parts.append(f"GSR at {gsr:.1f} (above 85 threshold)")
        if percentile and percentile >= 85.0:
            reasoning_parts.append(f"GSR at {percentile:.1f}th percentile")
        if z_score and z_score >= 1.5:
            reasoning_parts.append(f"Z-score {z_score:.2f} (>1.5 std above mean)")

        signals.append(
            Signal(
                signal_type="swap_gold_to_silver",
                strength=strength,
                gsr_value=gsr,
                gsr_percentile=percentile or 0.0,
                gsr_z_score=z_score or 0.0,
                macro_regime=regime_type,
                recommendation=f"Consider rotating {position_size:.1f}% of gold holdings to silver",
                position_size=position_size,
                reasoning="; ".join(reasoning_parts),
                timestamp=gsr_analysis["timestamp"],
            )
        )

    # Low GSR signal (swap silver -> gold)
    elif gsr <= 65.0 or (percentile is not None and percentile <= 20.0):
        strength = calculate_signal_strength(gsr, z_score, percentile, "low")

        position_size = calculate_position_size(strength, gsr)

        reasoning_parts = []
        if gsr <= 65.0:
            reasoning_parts.append(f"GSR at {gsr:.1f} (below 65 threshold)")
        if percentile and percentile <= 20.0:
            reasoning_parts.append(f"GSR at {percentile:.1f}th percentile")
        if z_score and z_score <= -1.0:
            reasoning_parts.append(f"Z-score {z_score:.2f} (<-1.0 std below mean)")

        signals.append(
            Signal(
                signal_type="swap_silver_to_gold",
                strength=strength,
                gsr_value=gsr,
                gsr_percentile=percentile or 0.0,
                gsr_z_score=z_score or 0.0,
                macro_regime=regime_type,
                recommendation=f"Consider rotating {position_size:.1f}% of silver holdings to gold",
                position_size=position_size,
                reasoning="; ".join(reasoning_parts),
                timestamp=gsr_analysis["timestamp"],
            )
        )

    return signals


def calculate_signal_strength(
    gsr: float, z_score: Optional[float], percentile: Optional[float], signal_direction: str
) -> float:
    """
    Calculate signal strength (0-100) based on GSR statistics.

    Args:
        gsr: Current GSR value
        z_score: Z-score of GSR
        percentile: Percentile rank of GSR
        signal_direction: "high" or "low"

    Returns:
        Signal strength (0-100)
    """
    strength = 50.0  # Base strength

    if signal_direction == "high":
        # Higher GSR = stronger signal
        if gsr >= 90:
            strength += 20
        elif gsr >= 85:
            strength += 10

        if z_score is not None:
            if z_score >= 2.0:
                strength += 15
            elif z_score >= 1.5:
                strength += 10

        if percentile is not None:
            if percentile >= 95:
                strength += 15
            elif percentile >= 90:
                strength += 10

    else:  # low
        # Lower GSR = stronger signal
        if gsr <= 60:
            strength += 20
        elif gsr <= 65:
            strength += 10

        if z_score is not None:
            if z_score <= -1.5:
                strength += 15
            elif z_score <= -1.0:
                strength += 10

        if percentile is not None:
            if percentile <= 10:
                strength += 15
            elif percentile <= 20:
                strength += 10

    return min(100.0, max(0.0, strength))


def calculate_position_size(strength: float, gsr: float) -> float:
    """
    Calculate recommended position size based on signal strength.

    Args:
        strength: Signal strength (0-100)
        gsr: Current GSR value

    Returns:
        Position size as percentage (5-20%)
    """
    # Base size: 10%
    base_size = 10.0

    # Adjust based on strength
    if strength >= 80:
        return 20.0
    elif strength >= 70:
        return 15.0
    elif strength >= 60:
        return 12.5
    else:
        return 10.0


async def get_current_regime(db: AsyncSession) -> Optional[Regime]:
    """Get the current active macro regime."""
    result = await db.execute(
        select(Regime)
        .where(Regime.end_date.is_(None))
        .order_by(Regime.start_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_signal_history(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> List[Dict[str, Any]]:
    """
    Get historical signals (would be stored in a signals table in production).

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of historical signals
    """
    # Placeholder - in production, this would query a signals table
    return []
