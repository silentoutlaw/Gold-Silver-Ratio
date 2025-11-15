"""
FRED (Federal Reserve Economic Data) data source.
Fetches macro economic indicators from FRED API.
"""

from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
from fredapi import Fred

from app.ingestion.sources.base import DataSource, PriceData, MacroData
from app.core.config import settings


class FREDDataSource(DataSource):
    """FRED data source for macro economic indicators."""

    # FRED series codes for key indicators
    SERIES_CODES = {
        # Treasury Yields
        "DGS2": "2-Year Treasury Yield",
        "DGS10": "10-Year Treasury Yield",
        "DGS30": "30-Year Treasury Yield",
        # TIPS Yields (Real Yields)
        "DFII5": "5-Year TIPS Yield",
        "DFII10": "10-Year TIPS Yield",
        "DFII30": "30-Year TIPS Yield",
        # Inflation
        "CPIAUCSL": "CPI All Items",
        "CPILFESL": "CPI Less Food & Energy",
        "PCEPI": "PCE Price Index",
        "PCEPILFE": "PCE Less Food & Energy",
        # Dollar Index
        "DTWEXBGS": "Dollar Index (Broad)",
        # Fed Funds Rate
        "DFF": "Effective Fed Funds Rate",
        "DFEDTARU": "Fed Funds Target Rate Upper",
        "DFEDTARL": "Fed Funds Target Rate Lower",
        # Labor Market
        "UNRATE": "Unemployment Rate",
        "PAYEMS": "Nonfarm Payrolls",
        # Commodities
        "DCOILWTICO": "WTI Crude Oil",
        "DCOILBRENTEU": "Brent Crude Oil",
        "GASREGW": "Gas Prices",
        # Markets
        "SP500": "S&P 500",
        "VIXCLS": "VIX",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize FRED data source."""
        api_key = api_key or settings.fred_api_key
        if not api_key:
            raise ValueError("FRED API key not configured")

        super().__init__(api_key)
        self.client = Fred(api_key=api_key)

    def get_source_name(self) -> str:
        return "FRED"

    async def fetch_prices(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """
        FRED doesn't provide traditional price data.
        This method returns empty list - use fetch_macro_data instead.
        """
        return []

    async def fetch_macro_data(
        self,
        series_codes: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """
        Fetch macro data from FRED.

        Args:
            series_codes: List of FRED series codes (uses defaults if None)
            start_date: Start date for data
            end_date: End date for data

        Returns:
            List of MacroData objects
        """
        if series_codes is None:
            series_codes = list(self.SERIES_CODES.keys())

        if start_date is None:
            start_date = datetime.now() - timedelta(days=365 * 5)  # 5 years default

        if end_date is None:
            end_date = datetime.now()

        all_data = []

        # Fetch each series (FRED API doesn't have batch endpoint)
        for code in series_codes:
            try:
                # Run synchronous Fred API call in executor
                loop = asyncio.get_event_loop()
                series_data = await loop.run_in_executor(
                    None,
                    lambda: self.client.get_series(
                        code,
                        observation_start=start_date.strftime("%Y-%m-%d"),
                        observation_end=end_date.strftime("%Y-%m-%d"),
                    ),
                )

                # Convert to MacroData objects
                for date, value in series_data.items():
                    if value is not None and not (
                        isinstance(value, float) and value != value
                    ):  # Check for NaN
                        all_data.append(
                            MacroData(
                                code=code,
                                date=datetime.combine(date, datetime.min.time()),
                                value=float(value),
                                source=self.get_source_name(),
                            )
                        )

                self.logger.info(
                    f"Fetched {len(series_data)} points for {code} from FRED"
                )

                # Rate limiting - FRED allows 120 requests per minute
                await asyncio.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error fetching FRED series {code}: {e}")
                continue

        self.logger.info(f"Total FRED data points fetched: {len(all_data)}")
        return all_data

    async def get_latest_value(self, series_code: str) -> Optional[MacroData]:
        """
        Get the most recent value for a FRED series.

        Args:
            series_code: FRED series code

        Returns:
            MacroData object or None if not found
        """
        try:
            loop = asyncio.get_event_loop()
            series_data = await loop.run_in_executor(
                None, lambda: self.client.get_series(series_code)
            )

            if series_data.empty:
                return None

            latest_date = series_data.index[-1]
            latest_value = series_data.iloc[-1]

            if latest_value is None or (
                isinstance(latest_value, float) and latest_value != latest_value
            ):
                return None

            return MacroData(
                code=series_code,
                date=datetime.combine(latest_date, datetime.min.time()),
                value=float(latest_value),
                source=self.get_source_name(),
            )

        except Exception as e:
            self.logger.error(f"Error fetching latest FRED value for {series_code}: {e}")
            return None
