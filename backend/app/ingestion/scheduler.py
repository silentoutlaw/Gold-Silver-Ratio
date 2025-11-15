"""
Data ingestion scheduler.
Schedules and runs data fetching jobs at configured intervals.
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def run_daily_ingestion():
    """Run daily data ingestion job."""
    logger.info(f"Starting daily ingestion at {datetime.utcnow()}")

    try:
        from app.ingestion.coordinator import ingest_all_data

        result = await ingest_all_data()
        logger.info(f"Daily ingestion completed: {result}")

    except Exception as e:
        logger.error(f"Daily ingestion failed: {e}", exc_info=True)


async def run_metric_computation():
    """Run metric computation job after data ingestion."""
    logger.info(f"Starting metric computation at {datetime.utcnow()}")

    try:
        from app.services.metrics import compute_all_metrics

        result = await compute_all_metrics()
        logger.info(f"Metric computation completed: {result}")

    except Exception as e:
        logger.error(f"Metric computation failed: {e}", exc_info=True)


async def run_signal_generation():
    """Run signal generation after metrics are computed."""
    logger.info(f"Starting signal generation at {datetime.utcnow()}")

    try:
        from app.services.signals import generate_signals

        result = await generate_signals()
        logger.info(f"Signal generation completed: {result}")

    except Exception as e:
        logger.error(f"Signal generation failed: {e}", exc_info=True)


async def run_alert_check():
    """Check and trigger alerts."""
    logger.info(f"Starting alert check at {datetime.utcnow()}")

    try:
        from app.services.alerts import check_alerts

        result = await check_alerts()
        logger.info(f"Alert check completed: {result}")

    except Exception as e:
        logger.error(f"Alert check failed: {e}", exc_info=True)


def start_scheduler():
    """Start the ingestion scheduler."""
    if not settings.ingestion_schedule_enabled:
        logger.info("Ingestion scheduler disabled in settings")
        return

    # Daily ingestion job
    scheduler.add_job(
        run_daily_ingestion,
        CronTrigger(
            hour=settings.ingestion_daily_hour,
            minute=settings.ingestion_daily_minute,
            timezone=settings.ingestion_timezone,
        ),
        id="daily_ingestion",
        name="Daily data ingestion",
        replace_existing=True,
    )

    # Metric computation (5 minutes after ingestion)
    scheduler.add_job(
        run_metric_computation,
        CronTrigger(
            hour=settings.ingestion_daily_hour,
            minute=(settings.ingestion_daily_minute + 5) % 60,
            timezone=settings.ingestion_timezone,
        ),
        id="metric_computation",
        name="Metric computation",
        replace_existing=True,
    )

    # Signal generation (10 minutes after ingestion)
    scheduler.add_job(
        run_signal_generation,
        CronTrigger(
            hour=settings.ingestion_daily_hour,
            minute=(settings.ingestion_daily_minute + 10) % 60,
            timezone=settings.ingestion_timezone,
        ),
        id="signal_generation",
        name="Signal generation",
        replace_existing=True,
    )

    # Alert checks (every hour)
    scheduler.add_job(
        run_alert_check,
        CronTrigger(minute=0, timezone=settings.ingestion_timezone),
        id="alert_check",
        name="Alert checking",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Ingestion scheduler started")


def stop_scheduler():
    """Stop the ingestion scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Ingestion scheduler stopped")
