"""
Web scraper for gold and silver prices.
Fetches current spot prices from public websites without API keys.
"""

from typing import List, Optional
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

from app.ingestion.sources.base import DataSource, PriceData, MacroData


class GoldPriceScraper(DataSource):
    """Web scraper for gold and silver spot prices."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize scraper (no API key needed)."""
        super().__init__(api_key)

    def get_source_name(self) -> str:
        return "WebScraper"

    async def fetch_prices(
        self,
        symbols: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """
        Fetch current gold and silver prices from web scraping.
        Only provides current prices, not historical data.
        """
        all_data = []

        try:
            # Try goldprice.org first
            prices = await self._scrape_goldprice_org()
            if prices:
                all_data.extend(prices)
        except Exception as e:
            self.logger.error(f"goldprice.org scraping failed: {e}")

        if not all_data:
            try:
                # Fallback: try kitco.com
                prices = await self._scrape_kitco()
                if prices:
                    all_data.extend(prices)
            except Exception as e:
                self.logger.error(f"kitco.com scraping failed: {e}")

        if not all_data:
            try:
                # Fallback: try investing.com
                prices = await self._scrape_investing_com()
                if prices:
                    all_data.extend(prices)
            except Exception as e:
                self.logger.error(f"investing.com scraping failed: {e}")

        return all_data

    async def _scrape_goldprice_org(self) -> List[PriceData]:
        """Scrape prices from goldprice.org."""
        self.logger.info("Scraping goldprice.org...")

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with session.get(
                "https://goldprice.org/", headers=headers, timeout=10
            ) as response:
                if response.status != 200:
                    self.logger.warning(
                        f"goldprice.org returned status {response.status}"
                    )
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                prices = []
                timestamp = datetime.now()

                # Find gold price (usually in a div with specific ID or class)
                # This is an example - actual selectors may vary
                gold_elem = soup.find("span", {"id": "sp-bid"})
                if gold_elem:
                    gold_text = gold_elem.text.strip().replace(",", "")
                    gold_price = float(re.search(r"[\d.]+", gold_text).group())

                    prices.append(
                        PriceData(
                            symbol="XAU",
                            timestamp=timestamp,
                            close=gold_price,
                            source=self.get_source_name(),
                        )
                    )
                    self.logger.info(f"✓ Gold: ${gold_price}/oz")

                # Find silver price
                silver_elem = soup.find("span", {"id": "sp-silver"})
                if silver_elem:
                    silver_text = silver_elem.text.strip().replace(",", "")
                    silver_price = float(re.search(r"[\d.]+", silver_text).group())

                    prices.append(
                        PriceData(
                            symbol="XAG",
                            timestamp=timestamp,
                            close=silver_price,
                            source=self.get_source_name(),
                        )
                    )
                    self.logger.info(f"✓ Silver: ${silver_price}/oz")

                return prices

    async def _scrape_kitco(self) -> List[PriceData]:
        """Scrape prices from kitco.com."""
        self.logger.info("Scraping kitco.com...")

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with session.get(
                "https://www.kitco.com/", headers=headers, timeout=10
            ) as response:
                if response.status != 200:
                    return []

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                prices = []
                timestamp = datetime.now()

                # Example selectors - actual ones may vary
                gold_elem = soup.find("span", class_="gold-price")
                if gold_elem:
                    gold_text = gold_elem.text.strip().replace(",", "").replace("$", "")
                    try:
                        gold_price = float(re.search(r"[\d.]+", gold_text).group())
                        prices.append(
                            PriceData(
                                symbol="XAU",
                                timestamp=timestamp,
                                close=gold_price,
                                source=self.get_source_name(),
                            )
                        )
                        self.logger.info(f"✓ Gold: ${gold_price}/oz")
                    except:
                        pass

                silver_elem = soup.find("span", class_="silver-price")
                if silver_elem:
                    silver_text = (
                        silver_elem.text.strip().replace(",", "").replace("$", "")
                    )
                    try:
                        silver_price = float(re.search(r"[\d.]+", silver_text).group())
                        prices.append(
                            PriceData(
                                symbol="XAG",
                                timestamp=timestamp,
                                close=silver_price,
                                source=self.get_source_name(),
                            )
                        )
                        self.logger.info(f"✓ Silver: ${silver_price}/oz")
                    except:
                        pass

                return prices

    async def _scrape_investing_com(self) -> List[PriceData]:
        """Scrape prices from investing.com."""
        self.logger.info("Scraping investing.com...")

        prices = []
        timestamp = datetime.now()

        async with aiohttp.ClientSession() as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            # Try gold
            try:
                async with session.get(
                    "https://www.investing.com/currencies/xau-usd",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Look for price in the HTML
                        match = re.search(r'"last":(\d+\.?\d*)', html)
                        if match:
                            gold_price = float(match.group(1))
                            prices.append(
                                PriceData(
                                    symbol="XAU",
                                    timestamp=timestamp,
                                    close=gold_price,
                                    source=self.get_source_name(),
                                )
                            )
                            self.logger.info(f"✓ Gold: ${gold_price}/oz")
            except Exception as e:
                self.logger.error(f"Error scraping gold from investing.com: {e}")

            # Try silver
            try:
                async with session.get(
                    "https://www.investing.com/currencies/xag-usd",
                    headers=headers,
                    timeout=10,
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        match = re.search(r'"last":(\d+\.?\d*)', html)
                        if match:
                            silver_price = float(match.group(1))
                            prices.append(
                                PriceData(
                                    symbol="XAG",
                                    timestamp=timestamp,
                                    close=silver_price,
                                    source=self.get_source_name(),
                                )
                            )
                            self.logger.info(f"✓ Silver: ${silver_price}/oz")
            except Exception as e:
                self.logger.error(f"Error scraping silver from investing.com: {e}")

        return prices

    async def fetch_macro_data(
        self,
        series_codes: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """Scraper doesn't provide macro data."""
        return []

    async def get_latest_prices(
        self, symbols: Optional[List[str]] = None
    ) -> List[PriceData]:
        """Get latest prices (same as fetch_prices for scraper)."""
        return await self.fetch_prices(symbols)
