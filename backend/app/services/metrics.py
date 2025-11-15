"""
Metrics computation service.
Computes derived metrics like GSR, correlations, z-scores, rolling statistics, etc.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import AsyncSessionLocal
from app.db.models import (
    Asset,
    Price,
    DerivedMetric,
    MetricValue,
    MacroSeries,
    MacroValue,
)

logger = logging.getLogger(__name__)


async def compute_all_metrics() -> Dict[str, Any]:
    """
    Compute all derived metrics.

    Returns:
        Dictionary with computation statistics
    """
    logger.info("Starting metric computation")

    stats = {
        "start_time": datetime.now(),
        "gsr_computed": 0,
        "correlations_computed": 0,
        "rolling_stats_computed": 0,
        "errors": [],
    }

    async with AsyncSessionLocal() as db:
        try:
            # 1. Compute GSR (Gold-Silver Ratio)
            stats["gsr_computed"] = await compute_gsr(db)

            # 2. Compute rolling statistics for GSR
            stats["rolling_stats_computed"] = await compute_gsr_rolling_stats(db)

            # 3. Compute correlations
            stats["correlations_computed"] = await compute_correlations(db)

            stats["end_time"] = datetime.now()
            stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()

            logger.info(f"Metric computation completed: {stats}")

        except Exception as e:
            logger.error(f"Metric computation failed: {e}", exc_info=True)
            stats["errors"].append(str(e))

    return stats


async def compute_gsr(db: AsyncSession, days_back: int = 365) -> int:
    """
    Compute Gold-Silver Ratio.

    Args:
        db: Database session
        days_back: Number of days to compute

    Returns:
        Number of GSR data points computed
    """
    logger.info("Computing GSR")

    # Get gold prices (XAU)
    gold_result = await db.execute(
        select(Asset).where(Asset.symbol == "XAU")
    )
    gold_asset = gold_result.scalar_one_or_none()

    # Get silver prices (XAG)
    silver_result = await db.execute(
        select(Asset).where(Asset.symbol == "XAG")
    )
    silver_asset = silver_result.scalar_one_or_none()

    if not gold_asset or not silver_asset:
        logger.error("Gold or silver asset not found")
        return 0

    # Get prices for last N days
    start_date = datetime.now() - timedelta(days=days_back)

    # Fetch gold prices
    gold_prices_result = await db.execute(
        select(Price)
        .where(and_(Price.asset_id == gold_asset.id, Price.timestamp >= start_date))
        .order_by(Price.timestamp)
    )
    gold_prices = gold_prices_result.scalars().all()

    # Fetch silver prices
    silver_prices_result = await db.execute(
        select(Price)
        .where(and_(Price.asset_id == silver_asset.id, Price.timestamp >= start_date))
        .order_by(Price.timestamp)
    )
    silver_prices = silver_prices_result.scalars().all()

    if not gold_prices or not silver_prices:
        logger.warning("No price data found for gold or silver")
        return 0

    # Create DataFrames
    gold_df = pd.DataFrame(
        [(p.timestamp, p.close) for p in gold_prices], columns=["timestamp", "gold"]
    )
    silver_df = pd.DataFrame(
        [(p.timestamp, p.close) for p in silver_prices], columns=["timestamp", "silver"]
    )

    # Merge on timestamp
    merged = pd.merge(gold_df, silver_df, on="timestamp", how="inner")

    if merged.empty:
        logger.warning("No overlapping gold/silver price data")
        return 0

    # Compute GSR
    merged["gsr"] = merged["gold"] / merged["silver"]

    # Get or create GSR metric
    metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    gsr_metric = metric_result.scalar_one_or_none()

    if not gsr_metric:
        gsr_metric = DerivedMetric(
            name="GSR",
            description="Gold-Silver Ratio",
            computation_method="gold_price / silver_price",
        )
        db.add(gsr_metric)
        await db.flush()

    # Store GSR values
    count = 0
    for _, row in merged.iterrows():
        # Check if already exists
        existing = await db.execute(
            select(MetricValue).where(
                and_(
                    MetricValue.metric_id == gsr_metric.id,
                    MetricValue.timestamp == row["timestamp"],
                )
            )
        )

        if existing.scalar_one_or_none():
            continue

        metric_value = MetricValue(
            metric_id=gsr_metric.id,
            timestamp=row["timestamp"],
            value=float(row["gsr"]),
            metadata={
                "gold_price": float(row["gold"]),
                "silver_price": float(row["silver"]),
            },
        )
        db.add(metric_value)
        count += 1

    await db.commit()
    logger.info(f"Computed {count} GSR data points")
    return count


async def compute_gsr_rolling_stats(
    db: AsyncSession, windows: List[int] = [30, 90, 180, 365]
) -> int:
    """
    Compute rolling statistics for GSR (mean, std, z-score, percentiles).

    Args:
        db: Database session
        windows: List of window sizes in days

    Returns:
        Number of stat data points computed
    """
    logger.info("Computing GSR rolling statistics")

    # Get GSR metric
    metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    gsr_metric = metric_result.scalar_one_or_none()

    if not gsr_metric:
        logger.error("GSR metric not found")
        return 0

    # Get GSR values
    values_result = await db.execute(
        select(MetricValue)
        .where(MetricValue.metric_id == gsr_metric.id)
        .order_by(MetricValue.timestamp)
    )
    values = values_result.scalars().all()

    if not values:
        return 0

    # Create DataFrame
    df = pd.DataFrame(
        [(v.timestamp, v.value) for v in values], columns=["timestamp", "gsr"]
    )
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    count = 0

    for window in windows:
        # Rolling mean
        df[f"gsr_ma_{window}"] = df["gsr"].rolling(window=window).mean()

        # Rolling std
        df[f"gsr_std_{window}"] = df["gsr"].rolling(window=window).std()

        # Z-score
        df[f"gsr_zscore_{window}"] = (
            df["gsr"] - df[f"gsr_ma_{window}"]
        ) / df[f"gsr_std_{window}"]

        # Percentile rank
        df[f"gsr_percentile_{window}"] = (
            df["gsr"]
            .rolling(window=window)
            .apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1] * 100)
        )

        # Store metrics
        for metric_name in [
            f"gsr_ma_{window}",
            f"gsr_std_{window}",
            f"gsr_zscore_{window}",
            f"gsr_percentile_{window}",
        ]:
            # Get or create metric
            metric_result = await db.execute(
                select(DerivedMetric).where(DerivedMetric.name == metric_name)
            )
            metric = metric_result.scalar_one_or_none()

            if not metric:
                descriptions = {
                    "ma": f"{window}-day moving average of GSR",
                    "std": f"{window}-day standard deviation of GSR",
                    "zscore": f"{window}-day z-score of GSR",
                    "percentile": f"{window}-day percentile rank of GSR",
                }

                desc_key = metric_name.split("_")[2]  # Get 'ma', 'std', etc.
                metric = DerivedMetric(
                    name=metric_name,
                    description=descriptions.get(desc_key, metric_name),
                    computation_method=f"Rolling {window}-day window",
                )
                db.add(metric)
                await db.flush()

            # Store values
            for timestamp, value in df[metric_name].items():
                if pd.isna(value):
                    continue

                # Check if exists
                existing = await db.execute(
                    select(MetricValue).where(
                        and_(
                            MetricValue.metric_id == metric.id,
                            MetricValue.timestamp == timestamp,
                        )
                    )
                )

                if existing.scalar_one_or_none():
                    continue

                metric_value = MetricValue(
                    metric_id=metric.id,
                    timestamp=timestamp,
                    value=float(value),
                )
                db.add(metric_value)
                count += 1

    await db.commit()
    logger.info(f"Computed {count} rolling stat data points")
    return count


async def compute_correlations(
    db: AsyncSession, windows: List[int] = [30, 90, 180]
) -> int:
    """
    Compute rolling correlations between GSR and macro variables.

    Args:
        db: Database session
        windows: List of window sizes for rolling correlation

    Returns:
        Number of correlation data points computed
    """
    logger.info("Computing correlations")

    # Variables to correlate with GSR
    correlate_with = [
        "DGS10",  # 10-year yield
        "DTWEXBGS",  # Dollar index
        "CPIAUCSL",  # CPI
        "DCOILWTICO",  # WTI oil
        "SP500",  # S&P 500
        "VIXCLS",  # VIX
    ]

    # Get GSR data
    gsr_metric_result = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    gsr_metric = gsr_metric_result.scalar_one_or_none()

    if not gsr_metric:
        return 0

    gsr_values_result = await db.execute(
        select(MetricValue)
        .where(MetricValue.metric_id == gsr_metric.id)
        .order_by(MetricValue.timestamp)
    )
    gsr_values = gsr_values_result.scalars().all()

    gsr_df = pd.DataFrame(
        [(v.timestamp, v.value) for v in gsr_values], columns=["timestamp", "gsr"]
    )
    gsr_df.set_index("timestamp", inplace=True)

    count = 0

    for series_code in correlate_with:
        # Get macro series
        series_result = await db.execute(
            select(MacroSeries).where(MacroSeries.code == series_code)
        )
        series = series_result.scalar_one_or_none()

        if not series:
            continue

        # Get values
        values_result = await db.execute(
            select(MacroValue)
            .where(MacroValue.macro_series_id == series.id)
            .order_by(MacroValue.date)
        )
        values = values_result.scalars().all()

        if not values:
            continue

        # Create DataFrame
        macro_df = pd.DataFrame(
            [(v.date, v.value) for v in values], columns=["timestamp", series_code]
        )
        macro_df.set_index("timestamp", inplace=True)

        # Merge with GSR
        merged = gsr_df.join(macro_df, how="inner")

        if merged.empty:
            continue

        # Compute rolling correlations for each window
        for window in windows:
            metric_name = f"corr_gsr_{series_code}_{window}d"

            correlation = (
                merged["gsr"].rolling(window=window).corr(merged[series_code])
            )

            # Get or create metric
            metric_result = await db.execute(
                select(DerivedMetric).where(DerivedMetric.name == metric_name)
            )
            metric = metric_result.scalar_one_or_none()

            if not metric:
                metric = DerivedMetric(
                    name=metric_name,
                    description=f"{window}-day rolling correlation: GSR vs {series_code}",
                    computation_method=f"Pearson correlation over {window} days",
                )
                db.add(metric)
                await db.flush()

            # Store correlation values
            for timestamp, value in correlation.items():
                if pd.isna(value):
                    continue

                # Check if exists
                existing = await db.execute(
                    select(MetricValue).where(
                        and_(
                            MetricValue.metric_id == metric.id,
                            MetricValue.timestamp == timestamp,
                        )
                    )
                )

                if existing.scalar_one_or_none():
                    continue

                metric_value = MetricValue(
                    metric_id=metric.id,
                    timestamp=timestamp,
                    value=float(value),
                )
                db.add(metric_value)
                count += 1

    await db.commit()
    logger.info(f"Computed {count} correlation data points")
    return count


async def get_current_gsr_analysis(db: AsyncSession) -> Dict[str, Any]:
    """
    Get current GSR with full statistical analysis.

    Args:
        db: Database session

    Returns:
        Dictionary with current GSR analysis
    """
    # Get latest GSR
    gsr_metric = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    gsr_metric = gsr_metric.scalar_one_or_none()

    if not gsr_metric:
        return {}

    latest_gsr = await db.execute(
        select(MetricValue)
        .where(MetricValue.metric_id == gsr_metric.id)
        .order_by(MetricValue.timestamp.desc())
        .limit(1)
    )
    latest_gsr = latest_gsr.scalar_one_or_none()

    if not latest_gsr:
        return {}

    # Get 90-day z-score
    zscore_metric = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "gsr_zscore_90")
    )
    zscore_metric = zscore_metric.scalar_one_or_none()

    latest_zscore = None
    if zscore_metric:
        zscore_result = await db.execute(
            select(MetricValue)
            .where(MetricValue.metric_id == zscore_metric.id)
            .order_by(MetricValue.timestamp.desc())
            .limit(1)
        )
        latest_zscore = zscore_result.scalar_one_or_none()

    # Get 90-day percentile
    percentile_metric = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "gsr_percentile_90")
    )
    percentile_metric = percentile_metric.scalar_one_or_none()

    latest_percentile = None
    if percentile_metric:
        percentile_result = await db.execute(
            select(MetricValue)
            .where(MetricValue.metric_id == percentile_metric.id)
            .order_by(MetricValue.timestamp.desc())
            .limit(1)
        )
        latest_percentile = percentile_result.scalar_one_or_none()

    return {
        "gsr": latest_gsr.value,
        "timestamp": latest_gsr.timestamp,
        "z_score": latest_zscore.value if latest_zscore else None,
        "percentile": latest_percentile.value if latest_percentile else None,
        "gold_price": latest_gsr.metadata.get("gold_price") if latest_gsr.metadata else None,
        "silver_price": latest_gsr.metadata.get("silver_price") if latest_gsr.metadata else None,
    }
