import streamlit as st
from data_retrieval.alpaca_trader import AlpacaOrderExecutive

def render_portfolio_dashboard(config_payload: dict):
    """Renders account metrics inside the sidebar tab with direct row-by-row close buttons."""
    if not config_payload.get("show_portfolio"):
        return

    trader_executive = AlpacaOrderExecutive()
    
    st.markdown("#### 💵 Balance Metrics Summary")
    acct_summary = trader_executive.get_account_summary()
    holdings_df = trader_executive.get_active_portfolio()

    st.metric("Total Net Equity", f"${acct_summary['Equity']:,}")
    st.metric("Available Cash", f"${acct_summary['Cash']:,}")
    st.metric("Buying Power", f"${acct_summary['Buying Power']:,}")

    st.markdown("#### 📂 Active Positions Ledger")
    
    if not holdings_df.empty:
        # Loop through each row in the positions dataframe to render inline control buttons
        for idx, row in holdings_df.iterrows():
            ticker = row["Ticker"]
            shares = row["Shares"]
            pnl_val = row["PnL (%)"]
            
            # Style the PnL text string dynamically
            pnl_color = "#00cc66" if pnl_val >= 0 else "#ff3333"
            pnl_text = f"<span style='color:{pnl_color}; font-weight:bold;'>{'+' if pnl_val >= 0 else ''}{pnl_val}%</span>"
            
            with st.container(border=True):
                # 3-column structural row layout optimized for narrow sidebars
                col_info, col_pnl, col_action = st.columns([0.45, 0.30, 0.25])
                
                with col_info:
                    st.markdown(f"**{ticker}** <br><span style='color:#94a3b8;'>{shares} Shares</span>", unsafe_allow_html=True)
                with col_pnl:
                    st.markdown(f"Value:<br>{pnl_text}", unsafe_allow_html=True)
                with col_action:
                    st.markdown("<div style='margin-top:2px;'></div>", unsafe_allow_html=True)
                    # LIQUIDATE ACTION TRIGGER: Routes an immediate opposite order payload to flatten out the position
                    if st.button("❌", key=f"btn_liq_side_{ticker}_{idx}", help=f"Instantly liquidate all {shares} shares of {ticker}"):
                        with st.spinner("Flattening..."):
                            side_action = "sell" if shares > 0 else "buy"
                            res = trader_executive.execute_order(
                                ticker=ticker,
                                side=side_action,
                                qty=abs(shares),
                                order_type="market"
                            )
                        if res["success"]:
                            st.toast(f"✅ Flattened {ticker} position successfully!")
                            st.rerun()
                        else:
                            st.error(res["message"])
    else:
        st.caption("ℹ️ No open positions found inside your sandbox workspace.")
