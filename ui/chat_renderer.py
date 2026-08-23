import streamlit as st
from core.report_parser import ExecutiveReportParser

def render_chat_history():
    """Chronologically loops and draws historical messages with HTML styles onto active layouts."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "content" in message:
                rating_val = message.get("rating", None)
                styled_html = ExecutiveReportParser.convert_to_html(message["content"], rating_val)
                st.html(styled_html)
            else:
                st.write(message["content"])

def render_performance_metrics(perf_data: dict, ticker_symbol: str = ""):
    """FIXED: Stores execution metrics inside session state instead of rendering inline."""
    if not perf_data:
        return
        
    # Instantiate the state logging dictionary if not present
    if "telemetry_history" not in st.session_state:
        st.session_state["telemetry_history"] = {}
        
    # Commit the latest runs metrics using the ticker asset name mapping token key
    st.session_state["telemetry_history"][ticker_symbol] = {
        "cycle_time": perf_data.get("Total Cycle Time", 0),
        "income_node": perf_data.get("Income Analyst Node", 0),
        "balance_node": perf_data.get("Balance Analyst Node", 0),
        "cash_node": perf_data.get("Cash Flow Node", 0),
        "in_tokens": perf_data.get("Input Tokens", 0),
        "out_tokens": perf_data.get("Output Tokens", 0)
    }

def render_batch_summary():
    """Renders the final batch processing telemetry data in a persistent sticky container layout."""
    if "latest_batch_summary" not in st.session_state or not st.session_state["latest_batch_summary"]:
        return

    summary = st.session_state["latest_batch_summary"]
    
    with st.container():
        st.markdown('<div class="fixed-footer-container"></div>', unsafe_allow_html=True)
        col_text, col_dismiss = st.columns([0.85, 0.15])
        with col_text:
            st.markdown(
                f"🏁 **Batch Screening Matrix Complete** | Processed `{summary['count']}` assets "
                f"| 📥 **Total Input:** {summary['in_tokens']:,} tok | 📤 **Total Output:** {summary['out_tokens']:,} tok"
            )
        with col_dismiss:
            if st.button("❌ Dismiss Summary", key="btn_dismiss_batch_summary", width='stretch', type="primary"):
                st.session_state["latest_batch_summary"] = None
                st.rerun()
