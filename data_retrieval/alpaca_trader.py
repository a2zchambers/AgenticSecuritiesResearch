import pandas as pd
from data_retrieval.alpaca_client import AlpacaPaperClient

class AlpacaOrderExecutive:
    """Manages pure-HTTP order routing and captures portfolio holding states."""
    
    def __init__(self):
        self.client = AlpacaPaperClient()

    def execute_order(self, ticker: str, side: str, qty: int, order_type: str, limit_price: float = None) -> dict:
        """Places a Buy or Sell Market/Limit order natively via REST POST methods."""
        payload = {
            "symbol": ticker.strip().upper(),
            "qty": str(qty),
            "side": side.lower(),
            "type": order_type.lower(),
            "time_in_force": "gtc"
        }
        if order_type.lower() == "limit" and limit_price:
            payload["limit_price"] = str(limit_price)

        res = self.client.request("POST", "orders", json_data=payload)
        if res["success"]:
            return {"success": True, "message": f"Order executed: {side.upper()} {qty} shares of {ticker} via {order_type.upper()}."}
        return res

    def get_active_portfolio(self) -> pd.DataFrame:
        """Extracts open position vectors and formats them into a high-density dataframe."""
        res = self.client.request("GET", "positions")
        if not res["success"] or not res["data"]:
            return pd.DataFrame()

        data = []
        for p in res["data"]:
            data.append({
                "Ticker": p.get("symbol"),
                "Shares": int(p.get("qty", 0)),
                "Avg Entry ($)": round(float(p.get("avg_entry_price", 0)), 2),
                "Market Price ($)": round(float(p.get("current_price", 0)), 2),
                "Total Value ($)": round(float(p.get("market_value", 0)), 2),
                "Unrealized PnL ($)": round(float(p.get("unrealized_pl", 0)), 2),
                "PnL (%)": round(float(p.get("unrealized_plpc", 0)) * 100, 2)
            })
        return pd.DataFrame(data)

    def get_account_summary(self) -> dict:
        """Gathers active paper cash and equity metrics."""
        res = self.client.request("GET", "account")
        if res["success"]:
            acc = res["data"]
            return {
                "Equity": round(float(acc.get("equity", 100000.0)), 2),
                "Buying Power": round(float(acc.get("buying_power", 400000.0)), 2),
                "Cash": round(float(acc.get("cash", 100000.0)), 2)
            }
        return {"Equity": 100000.0, "Buying Power": 400000.0, "Cash": 100000.0}
