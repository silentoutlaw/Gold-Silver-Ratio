"""
Abstract base class for data sources.
All data source implementations inherit from this.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Price data point."""

    symbol: str
    timestamp: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float = 0.0
    volume: Optional[float] = None
    source: str = ""


@dataclass
class MacroData:
    """Macro economic data point."""

    code: str  # Series code (e.g., "DGS10" for 10-year treasury)
    date: datetime
    value: float
    source: str = ""
    release_time: Optional[datetime] = None


class DataSource(ABC):
    """Abstract base class for data sources."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize data source.

        Args:
            api_key: Optional API key for the data source
        """
        self.api_key = api_key
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def fetch_prices(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """
        Fetch price data for symbols.

        Args:
            symbols: List of symbol identifiers
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of PriceData objects

        Raises:
            Exception: If fetching fails
        """
        pass

    @abstractmethod
    async def fetch_macro_data(
        self,
        series_codes: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """
        Fetch macro economic data.

        Args:
            series_codes: List of series codes
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of MacroData objects

        Raises:
            Exception: If fetching fails
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this data source."""
        pass

    def validate_data(self, data: List[Any]) -> bool:
        """
        Validate fetched data.

        Args:
            data: List of data points to validate

        Returns:
            True if valid, False otherwise
        """
        if not data:
            self.logger.warning("No data returned")
            return False

        return True

    async def handle_rate_limit(self, retry_after: int):
        """
        Handle rate limiting.

        Args:
            retry_after: Seconds to wait before retrying
        """
        import asyncio

        self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
        await asyncio.sleep(retry_after)
