"""
Data ingestion coordinator.
Orchestrates data fetching from all sources and stores in database.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.db.models import Asset, Price, MacroSeries, MacroValue, AssetType
from app.ingestion.sources import (
    FREDDataSource,
    MetalsDataSource,
    YahooFinanceDataSource,
    CFTCDataSource,
    GoldPriceScraper,
    PriceData,
    MacroData,
)

logger = logging.getLogger(__name__)


async def ingest_all_data(days_back: int = 1) -> Dict[str, Any]:
    """
    Run full data ingestion from all sources.

    Args:
        days_back: Number of days to fetch (1 for daily updates, more for backfill)

    Returns:
        Dictionary with ingestion statistics
    """
    logger.info(f"Starting data ingestion for last {days_back} days")

    start_date = datetime.now() - timedelta(days=days_back)
    end_date = datetime.now()

    stats = {
        "start_time": datetime.now(),
        "metals_prices": 0,
        "etf_prices": 0,
        "macro_series": 0,
        "cot_data": 0,
        "errors": [],
    }

    async with AsyncSessionLocal() as db:
        try:
            # 1. Fetch metals prices (gold, silver, etc.)
            stats["metals_prices"] = await ingest_metals_prices(db, start_date, end_date)

            # 2. Fetch ETF and equity prices
            stats["etf_prices"] = await ingest_yahoo_prices(db, start_date, end_date)

            # 3. Fetch macro economic data from FRED
            stats["macro_series"] = await ingest_fred_data(db, start_date, end_date)

            # 4. Fetch CFTC COT data
            stats["cot_data"] = await ingest_cftc_data(db, start_date, end_date)

            stats["end_time"] = datetime.now()
            stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()

            logger.info(f"Data ingestion completed: {stats}")

        except Exception as e:
            logger.error(f"Data ingestion failed: {e}", exc_info=True)
            stats["errors"].append(str(e))

    return stats


async def ingest_metals_prices(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> int:
    """Ingest metals prices (gold, silver, platinum, palladium)."""
    logger.info("Ingesting metals prices")

    try:
        # Try web scraper first (no API key needed)
        logger.info("Using web scraper for metals prices...")
        source = GoldPriceScraper()
        prices = await source.fetch_prices(start_date=start_date, end_date=end_date)

        # If scraper fails, try MetalsDataSource (which will also try scraping as fallback)
        if not prices:
            logger.info("Scraper failed, trying MetalsDataSource...")
            source = MetalsDataSource()
            prices = await source.fetch_prices(start_date=start_date, end_date=end_date)

        count = await store_price_data(db, prices, AssetType.METAL)
        logger.info(f"Stored {count} metals price points")
        return count

    except Exception as e:
        logger.error(f"Error ingesting metals prices: {e}")
        return 0


async def ingest_yahoo_prices(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> int:
    """Ingest ETF and equity prices from Yahoo Finance."""
    logger.info("Ingesting Yahoo Finance data")

    try:
        source = YahooFinanceDataSource()
        prices = await source.fetch_prices(start_date=start_date, end_date=end_date)

        count = await store_price_data(db, prices, AssetType.ETF)
        logger.info(f"Stored {count} Yahoo Finance price points")
        return count

    except Exception as e:
        logger.error(f"Error ingesting Yahoo Finance data: {e}")
        return 0


async def ingest_fred_data(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> int:
    """Ingest macro economic data from FRED."""
    logger.info("Ingesting FRED macro data")

    try:
        source = FREDDataSource()
        macro_data = await source.fetch_macro_data(
            start_date=start_date, end_date=end_date
        )

        count = await store_macro_data(db, macro_data)
        logger.info(f"Stored {count} FRED macro data points")
        return count

    except Exception as e:
        logger.error(f"Error ingesting FRED data: {e}")
        return 0


async def ingest_cftc_data(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> int:
    """Ingest CFTC COT data."""
    logger.info("Ingesting CFTC COT data")

    try:
        source = CFTCDataSource()
        cot_data = await source.fetch_macro_data(
            start_date=start_date, end_date=end_date
        )

        count = await store_macro_data(db, cot_data)
        logger.info(f"Stored {count} CFTC COT data points")
        return count

    except Exception as e:
        logger.error(f"Error ingesting CFTC data: {e}")
        return 0


async def store_price_data(
    db: AsyncSession, prices: List[PriceData], asset_type: AssetType
) -> int:
    """
    Store price data in database.

    Args:
        db: Database session
        prices: List of PriceData objects
        asset_type: Type of asset

    Returns:
        Number of records stored
    """
    count = 0

    for price in prices:
        try:
            # Get or create asset
            result = await db.execute(select(Asset).where(Asset.symbol == price.symbol))
            asset = result.scalar_one_or_none()

            if not asset:
                asset = Asset(
                    symbol=price.symbol,
                    name=price.symbol,  # Will be updated with proper name later
                    type=asset_type,
                    source=price.source,
                )
                db.add(asset)
                await db.flush()  # Get asset ID

            # Check if price already exists
            existing = await db.execute(
                select(Price).where(
                    Price.asset_id == asset.id, Price.timestamp == price.timestamp
                )
            )

            if existing.scalar_one_or_none():
                continue  # Skip duplicate

            # Create price record
            price_record = Price(
                asset_id=asset.id,
                timestamp=price.timestamp,
                open=price.open,
                high=price.high,
                low=price.low,
                close=price.close,
                volume=price.volume,
                source=price.source,
            )

            db.add(price_record)
            count += 1

        except Exception as e:
            logger.error(f"Error storing price {price.symbol} @ {price.timestamp}: {e}")
            continue

    await db.commit()
    return count


async def store_macro_data(db: AsyncSession, macro_data: List[MacroData]) -> int:
    """
    Store macro economic data in database.

    Args:
        db: Database session
        macro_data: List of MacroData objects

    Returns:
        Number of records stored
    """
    count = 0

    for data in macro_data:
        try:
            # Get or create macro series
            result = await db.execute(
                select(MacroSeries).where(MacroSeries.code == data.code)
            )
            series = result.scalar_one_or_none()

            if not series:
                series = MacroSeries(
                    code=data.code,
                    name=data.code,  # Will be updated with proper name later
                    source=data.source,
                    frequency="daily",
                )
                db.add(series)
                await db.flush()

            # Check if value already exists
            existing = await db.execute(
                select(MacroValue).where(
                    MacroValue.macro_series_id == series.id, MacroValue.date == data.date
                )
            )

            if existing.scalar_one_or_none():
                continue  # Skip duplicate

            # Create value record
            value_record = MacroValue(
                macro_series_id=series.id,
                date=data.date,
                value=data.value,
                release_time=data.release_time,
            )

            db.add(value_record)
            count += 1

        except Exception as e:
            logger.error(f"Error storing macro data {data.code} @ {data.date}: {e}")
            continue

    await db.commit()
    return count


async def backfill_historical_data(years: int = 5) -> Dict[str, Any]:
    """
    Backfill historical data for specified number of years.

    Args:
        years: Number of years of historical data to fetch

    Returns:
        Dictionary with backfill statistics
    """
    logger.info(f"Starting historical data backfill for {years} years")

    start_date = datetime.now() - timedelta(days=years * 365)
    end_date = datetime.now()

    # Run ingestion with longer time range
    stats = await ingest_all_data(days_back=years * 365)

    logger.info(f"Historical backfill completed: {stats}")
    return stats
