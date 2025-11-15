"""
Yahoo Finance data source.
Fetches ETF and equity data using yfinance.
"""

from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import asyncio
import pandas as pd

from app.ingestion.sources.base import DataSource, PriceData, MacroData


class YahooFinanceDataSource(DataSource):
    """Yahoo Finance data source for ETFs and equities."""

    # Key ETFs and indices to track
    SYMBOLS = {
        # Gold ETFs
        "GLD": "SPDR Gold Shares",
        "IAU": "iShares Gold Trust",
        "PHYS": "Sprott Physical Gold Trust",
        # Silver ETFs
        "SLV": "iShares Silver Trust",
        "PSLV": "Sprott Physical Silver Trust",
        # Mining ETFs
        "GDX": "VanEck Gold Miners ETF",
        "GDXJ": "VanEck Junior Gold Miners ETF",
        "SIL": "Global X Silver Miners ETF",
        "SILJ": "ETFMG Prime Junior Silver Miners ETF",
        # Indices
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones Industrial Average",
        "^IXIC": "NASDAQ Composite",
        "^VIX": "CBOE Volatility Index",
        # Currency ETFs
        "UUP": "Invesco DB USD Index Bullish",
        "FXE": "Invesco CurrencyShares Euro",
        # Commodity ETFs
        "USO": "United States Oil Fund",
        "UNG": "United States Natural Gas Fund",
        "COPX": "Global X Copper Miners ETF",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Yahoo Finance data source (no API key needed)."""
        super().__init__(api_key)

    def get_source_name(self) -> str:
        return "YahooFinance"

    async def fetch_prices(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """
        Fetch price data from Yahoo Finance.

        Args:
            symbols: List of ticker symbols
            start_date: Start date
            end_date: End date

        Returns:
            List of PriceData objects
        """
        if symbols is None:
            symbols = list(self.SYMBOLS.keys())

        if start_date is None:
            start_date = datetime.now() - timedelta(days=365 * 5)

        if end_date is None:
            end_date = datetime.now()

        all_data = []

        # yfinance is synchronous, so run in executor
        loop = asyncio.get_event_loop()

        for symbol in symbols:
            try:
                # Download data
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
                history = await loop.run_in_executor(
                    None,
                    lambda: ticker.history(
                        start=start_date.strftime("%Y-%m-%d"),
                        end=end_date.strftime("%Y-%m-%d"),
                    ),
                )

                if history.empty:
                    self.logger.warning(f"No data for {symbol}")
                    continue

                # Convert DataFrame to PriceData objects
                for date, row in history.iterrows():
                    # Handle pandas timestamp
                    if isinstance(date, pd.Timestamp):
                        timestamp = date.to_pydatetime()
                    else:
                        timestamp = date

                    all_data.append(
                        PriceData(
                            symbol=symbol,
                            timestamp=timestamp,
                            open=float(row["Open"]) if pd.notna(row["Open"]) else None,
                            high=float(row["High"]) if pd.notna(row["High"]) else None,
                            low=float(row["Low"]) if pd.notna(row["Low"]) else None,
                            close=float(row["Close"]) if pd.notna(row["Close"]) else 0.0,
                            volume=float(row["Volume"])
                            if pd.notna(row["Volume"])
                            else None,
                            source=self.get_source_name(),
                        )
                    )

                self.logger.info(f"Fetched {len(history)} points for {symbol}")

                # Small delay to be nice to Yahoo
                await asyncio.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error fetching Yahoo Finance data for {symbol}: {e}")
                continue

        self.logger.info(f"Total Yahoo Finance data points: {len(all_data)}")
        return all_data

    async def fetch_macro_data(
        self,
        series_codes: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """Yahoo Finance doesn't provide macro series."""
        return []

    async def get_latest_prices(
        self, symbols: Optional[List[str]] = None
    ) -> List[PriceData]:
        """
        Get latest prices for symbols.

        Args:
            symbols: List of ticker symbols

        Returns:
            List of latest PriceData objects
        """
        if symbols is None:
            symbols = list(self.SYMBOLS.keys())

        all_data = []
        loop = asyncio.get_event_loop()

        for symbol in symbols:
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, symbol)

                # Get last 2 days to ensure we have latest
                history = await loop.run_in_executor(
                    None, lambda: ticker.history(period="2d")
                )

                if history.empty:
                    continue

                # Get most recent
                last_row = history.iloc[-1]
                last_date = history.index[-1]

                if isinstance(last_date, pd.Timestamp):
                    timestamp = last_date.to_pydatetime()
                else:
                    timestamp = last_date

                all_data.append(
                    PriceData(
                        symbol=symbol,
                        timestamp=timestamp,
                        open=float(last_row["Open"])
                        if pd.notna(last_row["Open"])
                        else None,
                        high=float(last_row["High"])
                        if pd.notna(last_row["High"])
                        else None,
                        low=float(last_row["Low"])
                        if pd.notna(last_row["Low"])
                        else None,
                        close=float(last_row["Close"])
                        if pd.notna(last_row["Close"])
                        else 0.0,
                        volume=float(last_row["Volume"])
                        if pd.notna(last_row["Volume"])
                        else None,
                        source=self.get_source_name(),
                    )
                )

                await asyncio.sleep(0.2)

            except Exception as e:
                self.logger.error(
                    f"Error fetching latest Yahoo Finance data for {symbol}: {e}"
                )
                continue

        return all_data
