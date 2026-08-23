import streamlit as st
import pandas as pd
import re

from core.report_parser import ExecutiveReportParser
from core.chat_router import StrategicChatRouter
from core.orchestrator import ExecutionOrchestrator
from ui.sequential_runner import execute_sequential_screening
from ui.chat_renderer import render_chat_history, render_performance_metrics

class TradingUI:
    """Manages the layout configurations, top playground tab bars, and core sidebar interfaces."""

    @staticmethod
    def initialize_session_state(default_prompts: dict):
        """Ensures all session parameter values are instantiated to prevent rendering errors."""
        if "prompts" not in st.session_state:
            st.session_state.prompts = default_prompts.copy()
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Local desk online. Fundamental prompt modules loaded. How shall we direct the analyst team?"}
            ]
        if "telemetry_history" not in st.session_state:
            st.session_state["telemetry_history"] = {}

    @staticmethod
    def render_sidebar() -> dict:
        """Invokes our decoupled multi-tab sidebar control subpackage module."""
        from ui.ui_state import SessionStateManager
        return SessionStateManager.render_sidebar_controls()

    def render_fundamental_playground(self, config_payload: dict, orchestrator: ExecutionOrchestrator, router: StrategicChatRouter):
        """Renders the main content top navigation workspace tabs dashboard framework."""
        
        # Standard structural layout tab routing row arrays
        tab_research, tab_playground, tab_telemetry = st.tabs([
            "🔍 Corporate Screening Playground", 
            "🔮 Consensus Prompt Modules", 
            "📊 Session Telemetry"
        ])
        
        # --- TAB 1: CORPORATE RESEARCH PLAYGROUND PANEL (CONTAINS CHAT DISPATCH) ---
        with tab_research:
            st.markdown("### 💬 Strategy Chat Desk")
            
            # FIXED: Entire chronological message history stream is locked safely INSIDE Tab 1
            render_chat_history()
            
            # Handle real-time chat input specifically inside the Tab 1 boundary framework
            if user_input := st.chat_input("Ask a question, or type 'RUN RESEARCH' to start analysis...", key="chat_input_playground"):
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                cleaned_command = user_input.strip().upper()
                
                if cleaned_command in ["RUN", "RUN RESEARCH"]:
                    raw_tickers_string = config_payload.get("tickers_raw", config_payload.get("ticker", "AAPL"))
                    ticker_list = [t.strip().upper() for t in re.split(r'[,\s]+', raw_tickers_string) if t.strip()]
                    
                    if not ticker_list:
                        st.error("⚠️ No valid asset ticker symbols were detected within the configuration panels.")
                    else:
                        if config_payload.get("execution_mode") == "Parallel Threads":
                            from core.batch_runner import execute_parallel_screening
                            execute_parallel_screening(ticker_list, config_payload)
                        else:
                            execute_sequential_screening(ticker_list, config_payload, orchestrator)
                else:
                    # Standard Single Prompt routing path fallback logic
                    with st.chat_message("assistant"):
                        response_placeholder = st.empty()
                        answer_content, assigned_rating, perf_data = router.process_interaction(user_input, config_payload, response_placeholder)
                        st.session_state.messages.append({"role": "assistant", "content": answer_content, "rating": assigned_rating})
                        response_placeholder.html(ExecutiveReportParser.convert_to_html(answer_content, assigned_rating))
                        
                        single_ticker = config_payload.get("ticker", "AAPL").strip().upper()
                        render_performance_metrics(perf_data, ticker_symbol=single_ticker)
                        
                        # Auto-execution check for single query research submissions
                        if config_payload.get("auto_execute", False) and assigned_rating in ["STRONG BUY", "STRONG SELL"]:
                            from data_retrieval.alpaca_trader import AlpacaOrderExecutive
                            auto_trader = AlpacaOrderExecutive()
                            execution_qty = int(config_payload.get("auto_qty", 10))
                            trade_side = "buy" if assigned_rating == "STRONG BUY" else "sell"
                            
                            auto_trader.execute_order(ticker=single_ticker, side=trade_side, qty=execution_qty, order_type="market")
                            st.toast(f"🤖 Automated execution completed: {trade_side.upper()} {execution_qty} shares of {single_ticker}!")
                            
                        st.rerun()

        # --- TAB 2: AGENT CONFLICT PROMPT MODIFIERS PANEL ---
        with tab_playground:
            st.markdown("### 🔮 Fundamental Node Prompt Matrix Editor")
            st.caption("Live-tweak agent weights and critical text heuristics fed to OLLAMA parsing threads.")
            
            if "prompts" in st.session_state:
                with st.container(border=True):
                    all_prompts = st.session_state.prompts
                    for node_key, content in all_prompts.items():
                        st.session_state.prompts[node_key] = st.text_area(
                            f"🤖 Heuristics Vector Module: {node_key.replace('_', ' ').title()}",
                            value=content,
                            height=120,
                            key=f"txt_area_prompt_{node_key}"
                        )
                st.toast("🔮 Active agent text heuristic tokens matched to session matrices.")
            else:
                st.warning("⚠️ Session prompt configurations are currently uninitialized. Restart application daemon.")

        # --- TAB 3: CENTRALIZED SESSION PERFORMANCE TELEMETRY PANEL ---
        with tab_telemetry:
            # Invokes our decoupled centralized performance analytics drawing module cleanly
            from ui.telemetry_tab import render_telemetry_dashboard_tab
            render_telemetry_dashboard_tab()
