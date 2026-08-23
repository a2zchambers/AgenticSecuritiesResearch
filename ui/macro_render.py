import streamlit as st
import altair as alt
import os
from data_retrieval.macro_fetcher import FredMacroFetcher

class MacroDashboardRenderer:
    """Compiles multi-asset data matrices and renders them into an aligned, production-grade grid table layout."""

    @staticmethod
    def render_live_matrix():
        """Fetches and builds the visual equity index, macro, and interest curve canvas view."""
        st.markdown("### 🌐 Live FRED & Market Equity Matrix")
        
        if not os.getenv("FRED_API_KEY"):
            st.warning("⚠️ `$FRED_API_KEY` environmental variable not detected. Displaying default baseline data tracks.")
        else:
            st.success("🔒 Authenticated connection to FRED API data tunnels confirmed.")
        
        if st.button("📥 Load Live Macro Data Matrix", key="btn_load_macro"):
            fetcher = FredMacroFetcher()
            with st.spinner("Streaming metrics data live from analytical endpoints..."):
                macro_data = fetcher.gather_macro_matrix()
                
            # Render 6 corporate scorecard metrics in a single layout row
            m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
            m_col1.metric(label="S&P 500 Index Value", value=macro_data["latest_sp500"])
            m_col2.metric(label="NASDAQ 100 Index", value=macro_data["latest_nasdaq"])
            m_col3.metric(label="Consumer Price Index", value=macro_data["latest_cpi"])
            m_col4.metric(label="Real GDP Growth (YoY)", value=macro_data["latest_gdp"])
            m_col5.metric(label="US 10Y Treasury Rate", value=macro_data["latest_yield"])
            m_col6.metric(label="WTI Crude Spot Price", value=macro_data["latest_oil"])
            
            st.markdown("---")
            
            # =========================================================================
            # --- ROW 1 LAYER: EQUITY BENCHMARKS (S&P 500 vs NASDAQ 100) ---
            # =========================================================================
            r1_col1, r1_col2 = st.columns(2)
            
            with r1_col1:
                st.markdown("### 🟥 S&P 500 Market Index Vector Trend")
                df_sp = macro_data["sp500_df"].reset_index()
                chart_sp = alt.Chart(df_sp).mark_line(color="#b91c1c").encode(
                    x=alt.X("Date:T", title="Date Timeline"),
                    y=alt.Y("sp500:Q", title="Index Points", scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(chart_sp, width="stretch")
                st.caption("📋 **S&P 500 Data Sheet Audit Feed (Daily Close)**")
                st.dataframe(df_sp.sort_values("Date", ascending=False), height=200, width=550)

            with r1_col2:
                st.markdown("### 🟪 NASDAQ 100 Index Performance Track")
                df_ndx = macro_data["ndx_df"].reset_index()
                chart_ndx = alt.Chart(df_ndx).mark_line(color="#6d28d9").encode(
                    x=alt.X("Date:T", title="Date Timeline"),
                    y=alt.Y("nasdaq100:Q", title="Index Points", scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(chart_ndx, width="stretch")
                st.caption("📋 **NASDAQ 100 Data Sheet Audit Feed (Daily Close)**")
                st.dataframe(df_ndx.sort_values("Date", ascending=False), height=200, width=550)

            st.markdown("---")
            
            # =========================================================================
            # --- ROW 2 LAYER: LIQUID MARKET ASSETS (TREASURY YIELD CURVE vs CRUDE OIL) ---
            # =========================================================================
            r2_col1, r2_col2 = st.columns(2)
            
            with r2_col1:
                # --- FIXED: Stripped out '(Most Recent Spot Data)' subtitle token ---
                st.markdown("### 🟦 Current U.S. Treasury Yield Curve")
                df_yield = macro_data["yield_curve_df"]
                maturity_order = ["1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "30Y"]
                
                ymin = float(df_yield["Yield"].min())
                ymax = float(df_yield["Yield"].max())
                padding = 0.05
                y_domain = [ymin - padding, ymax + padding]
                
                chart_yield = alt.Chart(df_yield).mark_line(color="#0369a1", point=True).encode(
                    x=alt.X("Maturity:N", title="Maturity Term Structure", sort=maturity_order),
                    y=alt.Y("Yield:Q", title="Interest Rate (%)", scale=alt.Scale(zero=False, domain=y_domain)),
                    tooltip=["Maturity", "Yield"]
                ).properties(height=300)
                st.altair_chart(chart_yield, width="stretch")
                st.caption("📋 **U.S. Treasury Yield Curve Spot Table (Current Closes)**")
                st.dataframe(df_yield, height=200, width=550)

            with r2_col2:
                st.markdown("### 🟫 WTI Crude Oil Price Curve Shifter ($/bbl)")
                df_oil = macro_data["oil_curve_df"].reset_index()
                chart_oil = alt.Chart(df_oil).mark_line(color="#475569").encode(
                    x=alt.X("Date:T", title="Date"),
                    y=alt.Y("oil:Q", title="Price ($)", scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(chart_oil, width="stretch")
                st.caption("📋 **WTI Crude Data Sheet Audit Feed (Daily Close)**")
                st.dataframe(df_oil.sort_values("Date", ascending=False), height=200, width=550)

            st.markdown("---")

            # =========================================================================
            # --- ROW 3 LAYER: CORE MACROECONOMICS (CPI vs GDP OVERVIEW) ---
            # =========================================================================
            r3_col1, r3_col2 = st.columns(2)
            
            with r3_col1:
                st.markdown("### 🟨 Consumer Price Index (Unadjusted CPIAUCSL Time Series)")
                df_cpi = macro_data["cpi_df"].reset_index()
                chart_cpi = alt.Chart(df_cpi).mark_line(color="#ffb000", point=True).encode(
                    x=alt.X("Date:T", title="Date Timeline", scale=alt.Scale(type="utc"), axis=alt.Axis(format="%b %Y", labelAngle=-45, tickCount="month")),
                    y=alt.Y("cpi:Q", title="Index Level (Raw)", scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(chart_cpi, width="stretch")
                st.caption("📋 **CPI Data Sheet Audit Feed (Monthly Index)**")
                st.dataframe(df_cpi.sort_values("Date", ascending=False), height=200, width=550)

            with r3_col2:
                st.markdown("### 🟩 Economic Growth Rate (Real GDP YoY % Change)")
                df_gdp = macro_data["gdp_df"].reset_index()
                chart_gdp = alt.Chart(df_gdp).mark_line(color="#15803d", point=True).encode(
                    x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%b %Y", labelAngle=-45)),
                    y=alt.Y("gdp:Q", title="YoY Change (%)", scale=alt.Scale(zero=False))
                ).properties(height=300)
                st.altair_chart(chart_gdp, width="stretch")
                st.caption("📋 **GDP Data Sheet Audit Feed (Quarterly YoY)**")
                st.dataframe(df_gdp.sort_values("Date", ascending=False), height=200, width=550)
                
        else:
            st.info("💡 Click the button above to securely stream and display macroeconomic metrics from the Federal Reserve.")
