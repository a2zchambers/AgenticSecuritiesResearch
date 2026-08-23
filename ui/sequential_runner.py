import streamlit as st
import pandas as pd
import time
from core.report_parser import ExecutiveReportParser
from ui.chat_renderer import render_performance_metrics

def execute_sequential_screening(ticker_list: list, config_payload: dict, orchestrator):
    """Loops through ticker symbols sequentially to execute fundamental analysis graph loops."""
    init_broadcast = f"🚀 Instantiating sequential matrix scanning loop across {len(ticker_list)} assets one-by-one..."
    with st.chat_message("assistant"):
        st.markdown(init_broadcast)
    st.session_state.messages.append({"role": "assistant", "content": init_broadcast})
    
    with st.status("⚙️ Active Analysis Operations Log", expanded=True) as status:
        log_view = st.empty()
        log_messages = []
        
        def append_seq_log(text: str):
            log_messages.append(text)
            log_view.markdown("<br>".join(log_messages), unsafe_allow_html=True)

        footer_container = st.container()
        with footer_container:
            st.markdown('<div class="fixed-footer-container"></div>', unsafe_allow_html=True)
            progress_status_container = st.empty()
            batch_progress_bar = st.progress(0.0)
        
        total_symbols = len(ticker_list)
        seq_total_in_tokens = 0
        seq_total_out_tokens = 0
        
        for index, current_ticker in enumerate(ticker_list):
            pct_complete = index / total_symbols
            batch_progress_bar.progress(pct_complete)
            
            progress_status_container.markdown(
                f"📊 **Sequential Queue Status:** Processing `{current_ticker}` ({index + 1} of {total_symbols}) "
                f"| 📥 **In:** {seq_total_in_tokens:,} tok | 📤 **Out:** {seq_total_out_tokens:,} tok"
            )
            
            append_seq_log(f"🔄 `[{current_ticker}]` Spawning standalone fundamental matrix profile containers...")
            append_seq_log(f"📊 `[{current_ticker}]` Fetching quarterly ledger metrics via data streams...")
            
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.markdown(f"⏳ Generating fundamental consensus vector models for `{current_ticker}`...")
                
                try:
                    run_config = config_payload.copy()
                    run_config["ticker"] = current_ticker
                    
                    answer_content, assigned_rating, model_id, perf_data, seq_internal_logs = orchestrator.propagate_langgraph(
                        configs=run_config,
                        applied_prompts=st.session_state.prompts
                    )
                    
                    seq_total_in_tokens += perf_data.get("Input Tokens", 0)
                    seq_total_out_tokens += perf_data.get("Output Tokens", 0)
                    
                    for log_entry in seq_internal_logs:
                        append_seq_log(f"`[{current_ticker}]` {log_entry}")
                        
                    append_seq_log(f"✅ `[{current_ticker}]` Analysis step complete. Assigned Rating: `{assigned_rating}` ({perf_data.get('Total Cycle Time')}s)")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer_content,
                        "rating": assigned_rating
                    })
                    
                    final_styled_report = ExecutiveReportParser.convert_to_html(answer_content, assigned_rating)
                    response_placeholder.html(final_styled_report)
                    render_performance_metrics(perf_data, ticker_symbol=current_ticker)
                    
                    # -----------------------------------------------------------------
                    # 🤖 AUTO-EXECUTION SHIELD BLOCK FOR SEQUENTIAL TRACK
                    # -----------------------------------------------------------------
                    if config_payload.get("auto_execute", False):
                        if assigned_rating in ["STRONG BUY", "STRONG SELL"]:
                            append_seq_log(f"🤖 `[{current_ticker}]` Auto-Execute active! Routing order payload to Alpaca...")
                            from data_retrieval.alpaca_trader import AlpacaOrderExecutive
                            auto_trader = AlpacaOrderExecutive()
                            
                            # FIXED: Dynamically extracts the custom user selection input size allocation
                            execution_qty = int(config_payload.get("auto_qty", 10))
                            trade_side = "buy" if assigned_rating == "STRONG BUY" else "sell"
                            
                            auto_res = auto_trader.execute_order(
                                ticker=current_ticker,
                                side=trade_side,
                                qty=execution_qty,
                                order_type="market"
                            )
                            if auto_res["success"]:
                                append_seq_log(f"✅ `[{current_ticker}]` Automated trade executed: {trade_side.upper()} {execution_qty} shares of {current_ticker}.")
                            else:
                                append_seq_log(f"⚠️ `[{current_ticker}]` Auto-Trade refused: {auto_res['message']}")
                    
                except Exception as loop_error:
                    append_seq_log(f"❌ `[{current_ticker}]` Execution crashed: {str(loop_error)}")
                    error_fallback_text = f"❌ **Pipeline processing error discovered on symbol `{current_ticker}`:** `{str(loop_error)}`."
                    response_placeholder.markdown(error_fallback_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_fallback_text})
        
        status.update(label="🏁 Sequential Screening Loop Complete", state="complete", expanded=False)
    
    st.session_state["latest_batch_summary"] = {
        "count": total_symbols,
        "in_tokens": seq_total_in_tokens,
        "out_tokens": seq_total_out_tokens
    }
    
    batch_progress_bar.progress(1.0)
    progress_status_container.markdown("🏁 **All sequential loop tasks completed successfully.**")
    st.toast("✅ Sequential Portfolio Screening Cycle Complete.")
    st.rerun()
