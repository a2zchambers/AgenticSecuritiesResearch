import os
import json

class SectorLoader:
    """Handles thread-safe relative path parsing and inverse JSON asset mapping."""
    
    @staticmethod
    def load_sector_lookup() -> dict:
        """Loads sp500_sectors.json and inverts it into a rapid ticker-to-sector lookup dict."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_path = os.path.join(os.path.dirname(current_dir), "sp500_sectors.json")
            package_path = os.path.join(current_dir, "sp500_sectors.json")
            target_path = root_path if os.path.exists(root_path) else package_path

            if os.path.exists(target_path):
                with open(target_path, "r", encoding="utf-8") as f:
                    sector_map = json.load(f)
                
                # Formulate reverse tracking lookups
                inverted_map = {}
                for sector, tickers in sector_map.items():
                    for ticker in tickers:
                        inverted_map[ticker.strip().upper()] = sector
                return inverted_map
        except Exception:
            pass
        return {}
