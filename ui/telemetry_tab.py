import streamlit as st
import pandas as pd

def render_telemetry_dashboard_tab():
    """Renders all compiled node times and model token consumption tallies in a clean, scrollable log grid."""
    st.markdown("### 📊 Token Telemetry & Core Node Times Ledger")
    st.caption("Historical performance metrics tracking matrix across all assets analyzed during this desk session.")

    if "telemetry_history" not in st.session_state or not st.session_state["telemetry_history"]:
        st.info("ℹ️ No model execution runs completed yet. Execute analysis to populate these logs.")
        return

    # Transform our active memory dict state logs into an actionable dataframe matrix
    raw_history = st.session_state["telemetry_history"]
    table_rows = []
    
    for symbol, metrics in raw_history.items():
        table_rows.append({
            "Asset Ticker": symbol,
            "Total Run (s)": f"{metrics['cycle_time']}s",
            "Income Node": f"{metrics['income_node']}s",
            "Balance Node": f"{metrics['balance_node']}s",
            "Cash Node": f"{metrics['cash_node']}s",
            "Input Tokens": f"{metrics['in_tokens']:,}",
            "Output Tokens": f"{metrics['out_tokens']:,}"
        })
        
    df_telemetry = pd.DataFrame(table_rows)
    
    # Render structured high-density data matrix layout box frame
    st.dataframe(df_telemetry, width="stretch", height=280, hide_index=True)
    
    # Metric Accumulations Summary Bar Cards
    st.markdown("#### 📈 Cumulative Token Consumptions")
    t_in = sum([m["in_tokens"] for m in raw_history.values()])
    t_out = sum([m["out_tokens"] for m in raw_history.values()])
    
    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric("Total Session Input Tokens", f"{t_in:,} tok")
    with stat_col2:
        st.metric("Total Session Output Tokens", f"{t_out:,} tok")
        
    if st.button("🧹 Clear Telemetry History Ledger", width="stretch", type="secondary"):
        st.session_state["telemetry_history"] = {}
        st.rerun()
