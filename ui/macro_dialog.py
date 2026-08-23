import streamlit as st
import pandas as pd
from data_retrieval.macro_fetcher import FredMacroFetcher

@st.dialog("🏛️ Macro Indicator Analytics Viewer", width="large")
def show_macro_chart_modal(label: str, indicator_key: str):
    """Renders a historical timeline chart with a tightly scaled Y-axis alongside a clean pandas datatable."""
    st.caption(f"Historical telemetry tracking grid for macroeconomic parameter: **{label}**")
    
    fetcher = FredMacroFetcher()
    with st.spinner("⏳ Extracting time-series historical observations..."):
        df = fetcher.get_indicator_dataframe(indicator_key)
        
    if not df.empty:
        st.markdown(f"### 📈 {label} Trend")
        
        # --- TRACK A: TREASURY YIELD CURVE PLOT ---
        if indicator_key == "yield_curve":
            chart_df = df.copy()
            
            st.vega_lite_chart(
                chart_df,
                spec={
                    "mark": {"type": "line", "point": True, "color": "#ffb000"},
                    "encoding": {
                        "x": {"field": "Maturity", "type": "nominal", "title": "Curve Maturity Spectrum", "sort": None},
                        "y": {
                            "field": "Yield (%)", 
                            "type": "quantitative", 
                            "title": "Par Yield Rate (%)",
                            "scale": {"zero": False}
                        }
                    }
                },
                width="stretch"
            )
            
            st.markdown("### 📊 Active Spot Matrix Yields Table")
            st.dataframe(df, width='stretch', hide_index=True)
            
        # --- TRACK B: DAILY TIME-SERIES PLOTS (OIL, USD SPOT INDEX, SP500, NASDAQ) ---
        else:
            chart_df = df.copy()
            
            # FIXED: Dynamically extract the correct active non-date data column name string
            non_date_cols = [col for col in chart_df.columns if col != "Date"]
            
            # BULLETPROOF REFACTOR: Isolate the absolute exact first string key element name.
            # Vega-Lite requires a direct single-string key name; passing a list mapping index array 
            # like `non_date_cols` directly into the "field" layout property breaks silently!
            active_value_col = non_date_cols[0] if non_date_cols else "Value"
            
            st.vega_lite_chart(
                chart_df,
                spec={
                    "mark": {"type": "line", "color": "#00d4ff"},
                    "encoding": {
                        "x": {"field": "Date", "type": "temporal", "title": "Timeline Horizon"},
                        "y": {
                            # Explicitly mapping raw single string identifier tokens prevents rendering gaps
                            "field": str(active_value_col), 
                            "type": "quantitative", 
                            "title": str(active_value_col),
                            "scale": {"zero": False}  # Auto-scales axis bounds directly to match daily margins
                        }
                    }
                },
                width="stretch"
            )
            
            st.markdown("### 📊 Historical Observations Ledger")
            display_df = df.sort_values("Date", ascending=False).copy()
            display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%Y-%m-%d")
            st.dataframe(display_df, width='stretch', height=350, hide_index=True)
    else:
        st.error("❌ Unable to compile observations ledger for the target parameter model.")
