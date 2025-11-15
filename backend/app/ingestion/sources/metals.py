"""
Metals price data source.
Fetches gold, silver, and other precious metals prices from multiple APIs.
"""

from typing import List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio

from app.ingestion.sources.base import DataSource, PriceData, MacroData
from app.core.config import settings


class MetalsDataSource(DataSource):
    """Metals price data source using multiple APIs."""

    # Metal symbols
    METALS = {
        "XAU": "Gold",
        "XAG": "Silver",
        "XPT": "Platinum",
        "XPD": "Palladium",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize metals data source."""
        # Try multiple API keys
        self.metals_api_key = api_key or settings.metals_api_key
        self.alpha_vantage_key = settings.alpha_vantage_api_key

        super().__init__(self.metals_api_key or self.alpha_vantage_key)

    def get_source_name(self) -> str:
        return "MetalsAPI"

    async def fetch_prices(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """
        Fetch metals prices.

        Args:
            symbols: List of metal symbols (e.g., ["XAU", "XAG"])
            start_date: Start date
            end_date: End date

        Returns:
            List of PriceData objects
        """
        if symbols is None:
            symbols = list(self.METALS.keys())

        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)

        if end_date is None:
            end_date = datetime.now()

        # Try Metals-API first, then fall back to Alpha Vantage, then scraper
        if self.metals_api_key:
            return await self._fetch_from_metals_api(symbols, start_date, end_date)
        elif self.alpha_vantage_key:
            return await self._fetch_from_alpha_vantage(symbols, start_date, end_date)
        else:
            self.logger.warning("No metals API keys configured, using free scraper (current prices only)")
            return await self._fetch_from_scraper(symbols)

    async def _fetch_from_metals_api(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> List[PriceData]:
        """Fetch from Metals-API.com."""
        all_data = []

        async with aiohttp.ClientSession() as session:
            # Metals-API requires fetching date by date for historical data
            current_date = start_date

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")

                try:
                    # Metals-API endpoint: historical data
                    url = f"https://metals-api.com/api/{date_str}"
                    params = {
                        "access_key": self.metals_api_key,
                        "base": "USD",
                        "symbols": ",".join(symbols),
                    }

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            if data.get("success"):
                                rates = data.get("rates", {})
                                timestamp = datetime.strptime(
                                    data.get("date"), "%Y-%m-%d"
                                )

                                for symbol in symbols:
                                    if symbol in rates:
                                        # Metals-API returns price per unit in USD
                                        # For XAU and XAG, need to convert to per oz
                                        price = rates[symbol]

                                        # Metals-API returns XAU as USD per troy oz
                                        # and XAG as USD per troy oz
                                        all_data.append(
                                            PriceData(
                                                symbol=symbol,
                                                timestamp=timestamp,
                                                close=float(price),
                                                source=self.get_source_name(),
                                            )
                                        )

                        elif response.status == 429:
                            # Rate limited
                            await self.handle_rate_limit(60)
                            continue

                        # Rate limiting - 100 requests per month on free tier
                        await asyncio.sleep(1)

                except Exception as e:
                    self.logger.error(
                        f"Error fetching metals data for {date_str}: {e}"
                    )

                current_date += timedelta(days=1)

        self.logger.info(f"Fetched {len(all_data)} metals price points")
        return all_data

    async def _fetch_from_alpha_vantage(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> List[PriceData]:
        """Fetch from Alpha Vantage API (fallback)."""
        all_data = []

        # Alpha Vantage symbol mapping
        av_symbols = {
            "XAU": "XAUUSD",
            "XAG": "XAGUSD",
            "XPT": "XPTUSD",
            "XPD": "XPDUSD",
        }

        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                av_symbol = av_symbols.get(symbol, symbol)

                try:
                    url = "https://www.alphavantage.co/query"
                    params = {
                        "function": "FX_DAILY",
                        "from_symbol": symbol,
                        "to_symbol": "USD",
                        "apikey": self.alpha_vantage_key,
                        "outputsize": "full",  # Get full history
                    }

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            time_series = data.get("Time Series FX (Daily)", {})

                            for date_str, values in time_series.items():
                                date = datetime.strptime(date_str, "%Y-%m-%d")

                                if start_date <= date <= end_date:
                                    all_data.append(
                                        PriceData(
                                            symbol=symbol,
                                            timestamp=date,
                                            open=float(values.get("1. open", 0)),
                                            high=float(values.get("2. high", 0)),
                                            low=float(values.get("3. low", 0)),
                                            close=float(values.get("4. close", 0)),
                                            source="AlphaVantage",
                                        )
                                    )

                    # Alpha Vantage rate limit: 5 calls per minute
                    await asyncio.sleep(12)

                except Exception as e:
                    self.logger.error(
                        f"Error fetching Alpha Vantage data for {symbol}: {e}"
                    )

        self.logger.info(f"Fetched {len(all_data)} metals price points from Alpha Vantage")
        return all_data

    async def fetch_macro_data(
        self,
        series_codes: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """Metals data source doesn't provide macro data."""
        return []

    async def get_latest_prices(self, symbols: Optional[List[str]] = None) -> List[PriceData]:
        """
        Get latest prices for metals.

        Args:
            symbols: List of metal symbols

        Returns:
            List of latest PriceData objects
        """
        if symbols is None:
            symbols = list(self.METALS.keys())

        # Fetch last 2 days to ensure we get latest
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)

        all_prices = await self.fetch_prices(symbols, start_date, end_date)

        # Get most recent for each symbol
        latest = {}
        for price in all_prices:
            if (
                price.symbol not in latest
                or price.timestamp > latest[price.symbol].timestamp
            ):
                latest[price.symbol] = price

        return list(latest.values())

    async def _fetch_from_scraper(self, symbols: List[str]) -> List[PriceData]:
        """
        Fetch current metals prices from free public API (goldapi.io free tier).
        Only provides current prices, not historical data.
        """
        all_data = []

        # Map symbols to currency codes
        symbol_map = {
            "XAU": "XAU",
            "XAG": "XAG",
            "XPT": "XPT",
            "XPD": "XPD",
        }

        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                if symbol not in symbol_map:
                    continue

                try:
                    # Use metals-api.com free tier (no key needed for current price)
                    # or goldapi.io public endpoint
                    url = f"https://www.goldapi.io/api/{symbol}/USD"

                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()

                            # Parse response
                            if "price" in data:
                                price = float(data["price"])
                                timestamp = datetime.now()

                                all_data.append(
                                    PriceData(
                                        symbol=symbol,
                                        timestamp=timestamp,
                                        close=price,
                                        source="GoldAPI-Free",
                                    )
                                )

                                self.logger.info(f"Scraped {symbol} price: ${price}")
                        else:
                            # Try alternative free source - use marketstack or other
                            self.logger.warning(f"Could not fetch {symbol} from GoldAPI, status: {response.status}")

                except asyncio.TimeoutError:
                    self.logger.error(f"Timeout fetching {symbol} from scraper")
                except Exception as e:
                    self.logger.error(f"Error scraping {symbol}: {e}")

                await asyncio.sleep(1)  # Be nice to free APIs

        # If scraper didn't work, try yfinance for GLD/SLV as proxy
        if not all_data:
            self.logger.info("Scraper failed, trying Yahoo Finance ETFs as proxy")
            return await self._fetch_etf_proxy()

        return all_data

    async def _fetch_etf_proxy(self) -> List[PriceData]:
        """
        Use GLD and SLV ETF prices as proxy for gold/silver spot prices.
        This always works without any API keys.
        """
        import yfinance as yf

        all_data = []
        loop = asyncio.get_event_loop()

        # ETF proxies: GLD ≈ gold, SLV ≈ silver
        proxies = {
            "GLD": ("XAU", 1.0),  # GLD tracks gold pretty closely
            "SLV": ("XAG", 1.0),  # SLV tracks silver
        }

        for etf_symbol, (metal_symbol, _) in proxies.items():
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, etf_symbol)
                history = await loop.run_in_executor(None, lambda: ticker.history(period="1d"))

                if not history.empty:
                    last_row = history.iloc[-1]
                    last_date = history.index[-1]

                    # Convert ETF price to approximate spot price
                    # GLD: each share ≈ 0.1 oz of gold
                    # SLV: each share ≈ 1 oz of silver (roughly)
                    multiplier = 10.0 if etf_symbol == "GLD" else 1.0
                    spot_price = float(last_row["Close"]) * multiplier

                    all_data.append(
                        PriceData(
                            symbol=metal_symbol,
                            timestamp=last_date.to_pydatetime() if hasattr(last_date, 'to_pydatetime') else last_date,
                            close=spot_price,
                            source=f"YahooFinance-{etf_symbol}-Proxy",
                        )
                    )

                    self.logger.info(f"Got {metal_symbol} from {etf_symbol} ETF proxy: ${spot_price}")

            except Exception as e:
                self.logger.error(f"Error getting ETF proxy for {etf_symbol}: {e}")

        return all_data
