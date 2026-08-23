import streamlit as st
import sqlite3
import pandas as pd

def render_historical_explorer(orchestrator):
    """Renders an interactive database search UI targeting archived transaction summaries."""
    st.markdown("---")
    st.subheader("🔍 Historical Record Explorer")
    st.caption("Query the background SQLite storage layers directly to cross-reference archived agent evaluation metrics.")

    # Ticker input search box parameter layout
    lookup_ticker = st.text_input("Filter historical runs by Ticker symbol (leave blank for all records):", value="").strip().upper()

    try:
        db_file_path = getattr(orchestrator, "db_path", "trading_results.db")
        conn = sqlite3.connect(db_file_path)
        
        # CHANGED: Added model_used to the SQL select statements
        if lookup_ticker:
            query = "SELECT date, time, ticker, rating, reason, model_used FROM trade_ratings WHERE ticker = ? ORDER BY id DESC"
            df = pd.read_sql_query(query, conn, params=(lookup_ticker,))
        else:
            query = "SELECT date, time, ticker, rating, reason, model_used FROM trade_ratings ORDER BY id DESC LIMIT 50"
            df = pd.read_sql_query(query, conn)
            
        conn.close()
        
        if not df.empty:
            # Map structural columns out to corporate headers cleanly
            df.columns = ["Date", "Time", "Asset Ticker", "Consensus Rating", "Full Analysis Text", "Model Instance"]
            
            # CHANGED: Replaced use_container_width=True with width='stretch'
            st.dataframe(df, width='stretch', hide_index=True)
        else:
            st.info("ℹ️ No historical records discovered matching the active search parameters.")
            
    except Exception as db_ex:
        st.error(f"⚠️ **Unable to interface with local historical database layer:** `{str(db_ex)}`")
