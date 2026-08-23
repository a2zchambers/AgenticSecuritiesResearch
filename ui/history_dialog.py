import sqlite3
from datetime import datetime, date
import streamlit as st
import pandas as pd

@st.dialog("🏛️ Historical Record Explorer", width="large")
def show_history_modal(orchestrator):
    """Renders the SQLite transaction summaries inside an isolated modal with advanced filters and auto-routing handles."""
    st.caption("Query the background SQLite storage layers directly to cross-reference archived agent evaluation metrics.")

    try:
        db_file_path = getattr(orchestrator, "db_path", "trading_results.db")
        conn = sqlite3.connect(db_file_path)
        query = "SELECT date, time, ticker, sector, rating, reason, model_used FROM trade_ratings ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            st.info("ℹ️ No historical records discovered matching the active search parameters.")
            return

        df["date_parsed"] = pd.to_datetime(df["date"], errors="coerce").dt.date

        st.markdown("### 🎛️ Search Filters")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            search_ticker = st.text_input("Asset Ticker Search:", value="").strip().upper()
            unique_sectors = ["All Sectors"] + sorted(list(df["sector"].dropna().unique()))
            selected_sector = st.selectbox("Filter by GICS Sector:", options=unique_sectors, index=0)
        with f_col2:
            valid_ratings = ["All Ratings", "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
            selected_rating = st.selectbox("Filter by Consensus Rating:", options=valid_ratings, index=0)
        with f_col3:
            min_date = df["date_parsed"].min() if not df["date_parsed"].isna().all() else date(2023, 1, 1)
            max_date = df["date_parsed"].max() if not df["date_parsed"].isna().all() else date.today()
            start_date = st.date_input("Start Date Profile Window:", value=min_date)
            end_date = st.date_input("End Date Profile Window:", value=max_date)

        filtered_df = df.copy()
        if search_ticker:
            filtered_df = filtered_df[filtered_df["ticker"].str.contains(search_ticker, na=False)]
        if selected_sector != "All Sectors":
            filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
        if selected_rating != "All Ratings":
            # FIXED: Corrected variable name from filtered_rating to selected_rating
            filtered_df = filtered_df[filtered_df["rating"] == selected_rating]
        filtered_df = filtered_df[(filtered_df["date_parsed"] >= start_date) & (filtered_df["date_parsed"] <= end_date)]
        filtered_df = filtered_df.drop(columns=["date_parsed"])

        st.markdown("---")
        
        if not filtered_df.empty:
            st.markdown(f"📊 **Filtered Records Discovered:** `{len(filtered_df)}` rows out of `{len(df)}` records.")
            
            with st.container(height=400):
                for idx, row in filtered_df.iterrows():
                    with st.container(border=True):
                        col_meta, col_btn = st.columns([0.75, 0.25])
                        with col_meta:
                            st.markdown(f"📅 **{row['date']} {row['time']}** | 🎯 **{row['ticker']}** ({row['sector']}) -> **{row['rating']}**")
                            st.caption(f"🤖 Model: {row['model_used']}")
                            
                            # NATIVE FIX: Use expander framework instead of button session loops to preserve modal visibility
                            with st.expander("🔗 View Full Report Details", expanded=False):
                                st.markdown("#### 📂 Complete Agent Evaluation Report")
                                st.info(f"**Execution Model Core:** {row['model_used']}")
                                st.markdown(f"**Analysis Framework & Rationalization:**\n\n{row['reason']}")

                        with col_btn:
                            # Keep the trade execution system routing through session_state
                            if st.button("🦅 Trade Asset", key=f"btn_trade_hist_{idx}", width="stretch", type="secondary"):
                                st.session_state["active_trade_intent"] = {
                                    "ticker": row['ticker'],
                                    "rating": row['rating']
                                }
                                st.rerun() # This execution should safely break the modal window on intent confirmation

        else:
            st.info("ℹ️ No historical database rows match your selected combination of query conditions.")
            
    except Exception as db_ex:
        st.error(f"⚠️ **Unable to interface with local historical database layer:** `{str(db_ex)}`")
