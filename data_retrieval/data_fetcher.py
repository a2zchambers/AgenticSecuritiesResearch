import yfinance as yf

class FundamentalDataFetcher:
    """Handles raw data ingestion from yfinance and formats it as Markdown payloads."""
    
    @staticmethod
    def fetch_quarterly_sheets(ticker: str) -> str:
        """Downloads and formats quarterly Income, Balance Sheet, and Cash Flow profiles."""
        ticker_obj = yf.Ticker(ticker)
        
        income_txt = ticker_obj.quarterly_income_stmt.head(10).to_markdown() if ticker_obj.quarterly_income_stmt is not None else "Unavailable"
        balance_txt = ticker_obj.quarterly_balance_sheet.head(10).to_markdown() if ticker_obj.quarterly_balance_sheet is not None else "Unavailable"
        cash_txt = ticker_obj.quarterly_cashflow.head(10).to_markdown() if ticker_obj.quarterly_cashflow is not None else "Unavailable"
        
        return (
            f"\n\n[RAW FINANCIAL SHEET CONTEXT ATTACHMENTS]\n"
            f"### INCOME STATEMENT METRICS:\n{income_txt}\n\n"
            f"### BALANCE SHEET METRICS:\n{balance_txt}\n\n"
            f"### CASH FLOW STATEMENT METRICS:\n{cash_txt}\n"
        )
