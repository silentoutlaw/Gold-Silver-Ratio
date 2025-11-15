"""Data source implementations."""

from app.ingestion.sources.base import DataSource, PriceData, MacroData
from app.ingestion.sources.fred import FREDDataSource
from app.ingestion.sources.metals import MetalsDataSource
from app.ingestion.sources.yahoo import YahooFinanceDataSource
from app.ingestion.sources.cftc import CFTCDataSource
from app.ingestion.sources.scraper import GoldPriceScraper

__all__ = [
    "DataSource",
    "PriceData",
    "MacroData",
    "FREDDataSource",
    "MetalsDataSource",
    "YahooFinanceDataSource",
    "CFTCDataSource",
    "GoldPriceScraper",
]
