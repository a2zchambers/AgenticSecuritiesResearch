import streamlit as st

# Local relative package dot-notation lookup pointing to your internal client modules
from data_retrieval.alpaca_trader import AlpacaOrderExecutive

@st.dialog("🦅 Alpaca Paper Trade Terminal", width="medium")
def show_order_placement_modal(ticker: str, consensus_rating: str = ""):
    """Renders trade configuration inputs to route orders to Alpaca with a protective header barrier."""
    
    # FIXED: Added explicit structural spacing markdown lines to prevent overlapping the main app tabs
    st.markdown("<div style='margin-top: -15px; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    st.markdown(f"### 📦 Position Setup: **{ticker}**")
    if consensus_rating:
        st.caption(f"System Consensus Assessment Recommendation: `{consensus_rating}`")
        
    executive = AlpacaOrderExecutive()
    account = executive.get_account_summary()
    
    # FIXED: Wrapped the account metrics inside a bounded bordered container box 
    # This shields the numbers, forcing Streamlit to isolate them away from background navigation layers.
    with st.container(border=True):
        st.markdown("##### 💵 Available Account Telemetry")
        st.markdown(
            f"• **Available Cash:** `${account['Cash']:,}`<br>"
            f"• **Buying Power:** `${account['Buying Power']:,}`",
            unsafe_allow_html=True
        )
    
    # Protective structural divider line
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    col_side, col_type = st.columns(2)
    with col_side:
        side = st.radio("Order Direction Action:", options=["Buy", "Sell"], key="alpaca_order_side")
    with col_type:
        order_type = st.radio("Execution Constraint Model:", options=["Market", "Limit"], key="alpaca_order_type")

    st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

    col_qty, col_price = st.columns(2)
    with col_qty:
        qty = st.number_input("Shares Quantity:", min_value=1, value=10, step=1, key="alpaca_order_qty")
    with col_price:
        limit_price = st.number_input(
            "Limit Price Target ($):", 
            min_value=0.01, 
            value=100.0, 
            step=0.50,
            disabled=(order_type == "Market"),
            key="alpaca_order_price"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Transmit Order Payload to Sandbox", width="stretch", type="primary", key="alpaca_btn_submit"):
        with st.spinner("Transmitting order payload vectors..."):
            res = executive.execute_order(
                ticker=ticker,
                side=side,
                qty=qty,
                order_type=order_type,
                limit_price=limit_price if order_type == "Limit" else None
            )
        if res["success"]:
            st.success(res["message"])
            st.toast("✅ Order transmitted successfully.")
            st.session_state["trigger_portfolio_refresh"] = True
            st.rerun()
        else:
            st.error(res["message"])
