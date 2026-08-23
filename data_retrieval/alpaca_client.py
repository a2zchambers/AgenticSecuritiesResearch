import os
import requests

class AlpacaPaperClient:
    """Interfaces with Alpaca's Paper Trading sandbox using pure HTTP REST architecture."""
    
    def __init__(self):
        self.key_id = os.getenv("ALPACA_API_KEY_ID", "YOUR_KEY_ID")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY", "YOUR_SECRET_KEY")
        self.base_url = "https://alpaca.markets"

    def get_headers(self) -> dict:
        """Returns standard security verification routing headers."""
        return {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
            "Content-Type": "application/json"
        }

    def request(self, method: str, endpoint: str, json_data: dict = None) -> dict:
        """Sends a robust network payload to Alpaca endpoints."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.get_headers(),
                json=json_data,
                timeout=10
            )
            # FIXED: Used an explicit list of acceptable HTTP status codes (200, 201, 204)
            success_codes = [200, 201, 204]
            if response.status_code in success_codes:
                return {"success": True, "data": response.json()}
            else:
                # Catch detailed internal Alpaca API fault notes safely
                try:
                    error_msg = response.json().get("message", response.text)
                except Exception:
                    error_msg = response.text
                return {"success": False, "message": f"Alpaca Refusal: {error_msg}"}
        except Exception as e:
            return {"success": False, "message": f"Network Fault: {str(e)}"}
