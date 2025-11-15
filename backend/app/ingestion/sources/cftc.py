"""
CFTC (Commodity Futures Trading Commission) data source.
Fetches Commitment of Traders (COT) reports for gold and silver futures.
"""

from typing import List, Optional
from datetime import datetime, timedelta
import aiohttp
import asyncio
import csv
import io

from app.ingestion.sources.base import DataSource, PriceData, MacroData


class CFTCDataSource(DataSource):
    """CFTC COT data source."""

    # CFTC commodity codes
    COMMODITY_CODES = {
        "GOLD": "088691",  # Gold futures
        "SILVER": "084691",  # Silver futures
    }

    # CFTC data URL
    COT_URL = "https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize CFTC data source (no API key needed)."""
        super().__init__(api_key)

    def get_source_name(self) -> str:
        return "CFTC"

    async def fetch_prices(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[PriceData]:
        """CFTC doesn't provide price data."""
        return []

    async def fetch_macro_data(
        self,
        series_codes: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[MacroData]:
        """
        Fetch COT data from CFTC.

        The COT data includes positioning of commercial traders, non-commercial traders,
        and non-reportables for gold and silver futures.

        Args:
            series_codes: List of commodity codes (uses defaults if None)
            start_date: Start date
            end_date: End date

        Returns:
            List of MacroData objects with COT positioning data
        """
        if series_codes is None:
            series_codes = list(self.COMMODITY_CODES.keys())

        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)

        if end_date is None:
            end_date = datetime.now()

        all_data = []

        # CFTC publishes data by year in ZIP files
        years = range(start_date.year, end_date.year + 1)

        async with aiohttp.ClientSession() as session:
            for year in years:
                try:
                    url = self.COT_URL.format(year=year)

                    # Note: Actual implementation would need to:
                    # 1. Download ZIP file
                    # 2. Extract CSV
                    # 3. Parse CSV for specific commodity codes
                    # 4. Filter by date range
                    # 5. Extract relevant columns (net positions, etc.)

                    # For now, placeholder implementation
                    self.logger.info(
                        f"Would fetch CFTC COT data for {year} from {url}"
                    )

                    # Simulate fetching weekly COT data
                    # In production, this would parse actual CFTC files
                    current_date = max(
                        start_date, datetime(year, 1, 1)
                    )
                    end_of_year = min(end_date, datetime(year, 12, 31))

                    # COT reports are published weekly on Fridays
                    while current_date <= end_of_year:
                        # Find next Friday
                        days_until_friday = (4 - current_date.weekday()) % 7
                        if days_until_friday == 0 and current_date.weekday() != 4:
                            days_until_friday = 7

                        current_date += timedelta(days=days_until_friday)

                        if current_date > end_of_year:
                            break

                        # Placeholder COT data
                        for commodity in series_codes:
                            # Store net speculative position as a macro series
                            all_data.append(
                                MacroData(
                                    code=f"COT_{commodity}_NET_SPEC",
                                    date=current_date,
                                    value=0.0,  # Would be actual net position
                                    source=self.get_source_name(),
                                )
                            )

                        current_date += timedelta(days=7)  # Next week

                except Exception as e:
                    self.logger.error(f"Error fetching CFTC data for {year}: {e}")
                    continue

        self.logger.info(f"Fetched {len(all_data)} CFTC COT data points")
        return all_data

    async def get_latest_cot_position(
        self, commodity: str = "GOLD"
    ) -> Optional[MacroData]:
        """
        Get the latest COT position for a commodity.

        Args:
            commodity: Commodity name ("GOLD" or "SILVER")

        Returns:
            MacroData with latest position or None
        """
        # Fetch last month of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        data = await self.fetch_macro_data([commodity], start_date, end_date)

        if not data:
            return None

        # Return most recent
        return max(data, key=lambda x: x.date)

    async def parse_cot_file(self, csv_content: str) -> List[MacroData]:
        """
        Parse CFTC COT CSV file content.

        Args:
            csv_content: CSV file content as string

        Returns:
            List of MacroData objects
        """
        data = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))

            for row in reader:
                # Extract relevant fields from CFTC format
                # This is a simplified example - actual CFTC format has many columns
                try:
                    report_date = datetime.strptime(
                        row.get("Report_Date_as_YYYY-MM-DD", ""), "%Y-%m-%d"
                    )

                    # For each commodity we track
                    for commodity, code in self.COMMODITY_CODES.items():
                        if row.get("CFTC_Contract_Market_Code") == code:
                            # Net non-commercial (speculative) positions
                            noncomm_long = float(
                                row.get("NonComm_Positions_Long_All", 0)
                            )
                            noncomm_short = float(
                                row.get("NonComm_Positions_Short_All", 0)
                            )
                            net_spec = noncomm_long - noncomm_short

                            data.append(
                                MacroData(
                                    code=f"COT_{commodity}_NET_SPEC",
                                    date=report_date,
                                    value=net_spec,
                                    source=self.get_source_name(),
                                )
                            )

                            # Commercial (hedger) positions
                            comm_long = float(row.get("Comm_Positions_Long_All", 0))
                            comm_short = float(row.get("Comm_Positions_Short_All", 0))
                            net_comm = comm_long - comm_short

                            data.append(
                                MacroData(
                                    code=f"COT_{commodity}_NET_COMM",
                                    date=report_date,
                                    value=net_comm,
                                    source=self.get_source_name(),
                                )
                            )

                except (ValueError, KeyError) as e:
                    continue

        except Exception as e:
            self.logger.error(f"Error parsing COT file: {e}")

        return data
