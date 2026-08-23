import streamlit as st
import pandas as pd

# Absolute modular imports from your decoupled sub-component namespace files
from ui.macro_dialog import show_macro_chart_modal
from ui.sector_tabs import SectorTabRenderer
from ui.portfolio_dashboard import render_portfolio_dashboard

class SessionStateManager:
    """Manages foundational multi-agent state initializations and interactive memory caches."""
    
    @staticmethod
    def initialize(default_prompts: dict):
        """Pre-populates prompt dictionaries and text history tracking variables."""
        if "prompts" not in st.session_state:
            st.session_state.prompts = default_prompts.copy()
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Local desk online. Fundamental prompt modules loaded. How shall we direct the analyst team?"}
            ]
        if "telemetry_history" not in st.session_state:
            st.session_state["telemetry_history"] = {}

    @staticmethod
    def render_sidebar_controls() -> dict:
        """Renders configuration fields and bundles values into clean multi-tab sidebar containers."""
        
        # Inserted a dedicated 🔍 Research sub-tab exactly before the Portfolio container
        tab_symbol, tab_macro, tab_research_archive, tab_portfolio, tab_utils = st.sidebar.tabs([
            "🎯 Symbol", 
            "🛢️ Macro", 
            "🔍 Research", 
            "💼 Portfolio", 
            "🛠️ Utils"
        ])
        
        # Load the external sp500_sectors.json repository registry matrix
        sector_map = SectorTabRenderer.read_sector_file()

        # Guarantee state checking list vectors are instantiated to block layout errors
        for sector_name in sector_map.keys():
            key_name = f"sel_{sector_name}"
            if key_name not in st.session_state:
                st.session_state[key_name] = []

        # --- TAB 1: ASSET SYMBOL TARGET SELECTION ---
        with tab_symbol:
            st.subheader("🎯 Target Portfolio Matrix")
            
            if st.button("🔄 Reset Selection Queue", width='stretch'):
                for sector_name in sector_map.keys():
                    st.session_state[f"sel_{sector_name}"] = []
                st.session_state["sb_tickers"] = ""
                st.rerun()

            all_selected_tickers = []
            for sector_name in sector_map.keys():
                key_name = f"sel_{sector_name}"
                all_selected_tickers.extend(st.session_state.get(key_name, []))
            
            all_selected_tickers = sorted(list(set(all_selected_tickers)))
            
            if all_selected_tickers:
                st.session_state["sb_tickers"] = " ".join(all_selected_tickers)
            elif "sb_tickers" not in st.session_state:
                st.session_state["sb_tickers"] = "AAPL MSFT GOOG"
            
            tickers_input = st.text_input(
                "Active Ticker Pipeline Queue (space or comma separated)", 
                key="sb_tickers"
            )
            
            current_today = pd.Timestamp.now()
            analysis_date = st.date_input("Target Analysis Date", value=current_today, key="sb_date")
            
            st.markdown("---")
            st.caption("📁 Toggle sector folders below to push asset presets into your queue:")
            SectorTabRenderer.render_symbol_selectors(sector_map)
        
        # --- TAB 2: MACROECONOMIC ASSUMPTIONS ---
        with tab_macro:
            st.subheader("🌐 Global Environment")
            macro_regime = st.selectbox("Macro Environment Baseline", ["Stagflationary", "Expansionary", "Disinflationary Peak"], key="sb_regime")
            
            st.markdown("---")
            st.subheader("🛢️ Systemic Parameters")
            
            col_oil_slider, col_oil_btn = st.columns([0.75, 0.25])
            with col_oil_slider:
                oil_price = st.slider("Crude Oil Price ($/bbl)", 40, 150, 75, key="sb_oil")
            with col_oil_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📈", key="btn_chart_oil", help="View Crude Oil Historical Trend Chart and Table"):
                    show_macro_chart_modal("WTI Crude Oil Price", "oil")

            col_yield_label, col_yield_btn = st.columns([0.75, 0.25])
            with col_yield_label:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("🇺🇸 **US Treasury Yield Curve Matrix**")
            with col_yield_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📈", key="btn_chart_yield", help="View Full US Treasury Yield Curve Chart and Table"):
                    show_macro_chart_modal("US Treasury Yield Curve Structure", "yield_curve")

            col_usd_slider, col_usd_btn = st.columns([0.75, 0.25])
            with col_usd_slider:
                usd_index_val = st.slider("USD Spot Index Baseline", 80, 160, 100, key="sb_usd_index")
            with col_usd_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📈", key="btn_chart_usd", help="View Real Broad USD Spot Index Historical Chart and Table"):
                    show_macro_chart_modal("Real Broad USD Spot Index", "usd_index")

            # --- MARKET EQUITY INDICES VIEWERS ---
            st.markdown("---")
            st.subheader("📊 Market Indices")
            
            col_sp_label, col_sp_btn = st.columns([0.75, 0.25])
            with col_sp_label:
                st.markdown("🎯 **S&P 500 Index**")
            with col_sp_btn:
                if st.button("📈", key="btn_chart_sp_fred", help="View S&P 500 Daily Chart"):
                    show_macro_chart_modal("S&P 500 Index", "sp500_fred")

            col_ns_label, col_ns_btn = st.columns([0.75, 0.25])
            with col_ns_label:
                st.markdown("🚀 **NASDAQ Composite Index**")
            with col_ns_btn:
                if st.button("📈", key="btn_chart_ns_fred", help="View NASDAQ Composite  Daily Chart"):
                    show_macro_chart_modal("NASDAQ Composite Index", "nasdaq_fred")

        # --- TAB 3: NEW RESEARCH ARCHIVES PANEL LOCATION ---
        with tab_research_archive:
            st.subheader("🏛️ Research Archives")
            st.caption("Access historical agent screening evaluations recorded inside the backend SQLite layers.")
            trigger_history_modal = st.button("🔍 Open Research Explorer", width='stretch', key="sb_btn_history")

        # --- TAB 4: SIDEBAR PORTFOLIO TERMINAL ---
        with tab_portfolio:
            st.subheader("🦅 Alpaca Paper Sandbox")
            show_portfolio = st.checkbox("🔌 Enable Terminal Tracking", value=True, key="sb_chk_portfolio")
            
            auto_execute = st.toggle("🤖 Auto-Execute Strong Ratings", value=False, key="sb_auto_execute", help="Automatically routes Market Orders to Alpaca when consensus returns STRONG BUY or STRONG SELL.")
            
            # NEW: Numerical default quantity selector box (clamped to a minimum of 1 share)
            auto_qty = st.number_input("Default Auto-Trade Shares Qty:", min_value=1, value=10, step=1, key="sb_auto_qty", help="The volume of shares the auto-trader will buy or sell when triggered.")
            
            if show_portfolio:
                from .portfolio_dashboard import render_portfolio_dashboard
                render_portfolio_dashboard({"show_portfolio": show_portfolio, "auto_execute": auto_execute})
        
        # --- TAB 5: UTILITIES & SYSTEM MANAGEMENT PANEL ---
        with tab_utils:
            st.markdown("---")
            st.subheader("🦙 Ollama Node Parameters")
            model_id = st.selectbox(
                "Active Local Model ID",
                ["muse-glimmer:30b-mlx", "qwen3:latest", "qwen2.5:7b", "llama3", "mistral", "phi3", "deepseek-r1:8b", "llama3.1"],
                key="sb_model_id"
            )
            endpoint = st.text_input("Ollama Endpoint URL", value="http://localhost:11434", key="sb_endpoint")
            
            st.markdown("---")
            st.subheader("⚙️ Execution Architecture")
            execution_mode = st.radio(
                "Multi-Ticker Processing Mode:",
                options=["Parallel Threads", "Sequential Loop"],
                index=1,
                help="Parallel tracks tokens concurrently using thread pools. Sequential loops through tickers one-by-one."
            )
            
            st.markdown("---")
            st.subheader("🧹 Maintenance")
            trigger_wipe_chat = st.button("Wipe Chat Research Logs", width='stretch', type="primary", key="sb_btn_wipe")
        
        # FIXED: Injected standard interest_rate mapping variable (defaults to standard 10Y Yield proxy value ~4.28)
        # to guarantee the backend graph thread orchestration contexts never crash with a KeyError.
        return {
            "model_id": model_id, 
            "endpoint": endpoint, 
            "tickers_raw": tickers_input, 
            "analysis_date": analysis_date, 
            "oil_price": oil_price, 
            "usd_index": usd_index_val,
            "interest_rate": 4.28,  # FIXED: Restored core parameter mapping
            "macro_regime": macro_regime,
            "trigger_history_modal": trigger_history_modal,
            "trigger_wipe_chat": trigger_wipe_chat,
            "show_portfolio": show_portfolio,
            "execution_mode": execution_mode
        }
