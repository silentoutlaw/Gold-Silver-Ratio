"""Data ingestion pipeline for GSR Analytics."""

from app.ingestion.scheduler import start_scheduler, stop_scheduler

__all__ = ["start_scheduler", "stop_scheduler"]
