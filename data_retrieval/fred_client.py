import os
import requests
import pandas as pd

class FredClient:
    """Handles raw network ingestion and metadata string conversions from the FRED API endpoints."""
    
    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")
        self.base_url = "https://stlouisfed.org"

    def has_valid_key(self) -> bool:
        """Returns True if a real structural API key token is discovered in env states."""
        return bool(self.api_key and self.api_key.strip() and self.api_key != "your_actual_fred_api_key")

    def fetch_series_raw(self, series_id: str, observation_start: str = "2022-01-01", limit: int = None, frequency: str = None) -> list:
        """Queries the raw JSON observation nodes straight from the FRED server."""
        if not self.has_valid_key():
            return []

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "observation_start": observation_start
        }
        if limit:
            params["limit"] = limit
        if frequency:
            params["frequency"] = frequency

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("observations", [])
        except Exception:
            pass
        return []

    def parse_observations(self, observations: list, label: str) -> pd.DataFrame:
        """Transforms raw string observation nodes into a sorted pandas DataFrame matrix."""
        dates, values = [], []
        for obs in observations:
            if obs.get("value") and obs["value"] != ".":
                try:
                    values.append(float(obs["value"]))
                    dates.append(pd.to_datetime(obs["date"]))
                except ValueError:
                    continue
                    
        if len(values) > 0:
            df = pd.DataFrame({"Date": dates, label: values})
            return df.sort_values("Date").drop_duplicates(subset=["Date"])
        return pd.DataFrame()
