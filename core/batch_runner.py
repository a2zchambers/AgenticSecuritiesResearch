import streamlit as st
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.orchestrator import ExecutionOrchestrator
from core.report_parser import ExecutiveReportParser
from ui.chat_renderer import render_performance_metrics

class ThreadLogBuffer:
    """Thread-safe, isolated memory writer to accumulate status logs inside worker threads."""
    def __init__(self, ticker):
        self.ticker = ticker
        self.buffer = []
    def write(self, text):
        self.buffer.append(text)

def _execute_thread_worker(ticker_symbol, base_config, prompts):
    """Safely executes the multi-agent graph with zero Streamlit context leaks using pure Python logging buffers."""
    logger = ThreadLogBuffer(ticker_symbol)
    try:
        thread_config = base_config.copy()
        thread_config["ticker"] = ticker_symbol
        
        logger.write("Instantiating structural financial matrix layers...")
        local_orchestrator = ExecutionOrchestrator()
        
        logger.write("Ingesting quarterly data profiles...")
        report, rating, model_id, perf_data, thread_logs = local_orchestrator.propagate_langgraph(
            configs=thread_config,
            applied_prompts=prompts
        )
        
        logger.write(f"Multi-agent synthesis complete. Consensus Rating assigned: `{rating}`.")
        combined_logs = logger.buffer + thread_logs
        return {
            "ticker": ticker_symbol, 
            "success": True, 
            "report": report, 
            "rating": rating, 
            "perf": perf_data,
            "logs": combined_logs
        }
    
    except BaseException as err:
        error_type, error_instance, error_trace = sys.exc_info()
        trace_summary = "".join(traceback.format_exception(error_type, error_instance, error_trace))
        return {
            "ticker": ticker_symbol, 
            "success": False, 
            "error": f"Internal System Context Crash: {str(err if str(err) else type(error_instance).__name__)}"
        }

def execute_parallel_screening(ticker_list: list, config_payload: dict):
    """Orchestrates an asynchronous thread pool to process massive ticker lists concurrently with operational logs."""
    init_broadcast = f"🚀 Instantiating parallel multi-threaded matrix scanning across {len(ticker_list)} assets concurrently..."
    with st.chat_message("assistant"):
        st.markdown(init_broadcast)
    st.session_state.messages.append({"role": "assistant", "content": init_broadcast})
    
    with st.status("⚙️ Active Analysis Operations Log", expanded=True) as status:
        log_view = st.empty()
        log_messages = []
        
        def append_log(text: str):
            log_messages.append(text)
            log_view.markdown("<br>".join(log_messages), unsafe_allow_html=True)

        footer_container = st.container()
        with footer_container:
            st.markdown('<div class="fixed-footer-container"></div>', unsafe_allow_html=True)
            progress_status_container = st.empty()
            batch_progress_bar = st.progress(0.0)
        
        total_symbols = len(ticker_list)
        completed_count = 0
        total_in_tokens = 0
        total_out_tokens = 0
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    _execute_thread_worker, ticker, config_payload, st.session_state.prompts
                ): ticker for ticker in ticker_list
            }
            
            for future in as_completed(futures):
                completed_count += 1
                res_data = future.result()
                current_ticker = res_data["ticker"]
                
                if res_data["success"]:
                    perf_data = res_data["perf"]
                    total_in_tokens += perf_data.get("Input Tokens", 0)
                    total_out_tokens += perf_data.get("Output Tokens", 0)
                    
                    for log_entry in res_data.get("logs", []):
                        append_log(f"⚙️ **`[{current_ticker}]`** {log_entry}")
                
                pct_complete = completed_count / total_symbols
                batch_progress_bar.progress(pct_complete)
                
                progress_status_container.markdown(
                    f"📊 **Parallel Queue Status:** Processed `{current_ticker}` ({completed_count} of {total_symbols}) "
                    f"| 📥 **In:** {total_in_tokens:,} tok | 📤 **Out:** {total_out_tokens:,} tok"
                )
                
                with st.chat_message("assistant"):
                    if res_data["success"]:
                        answer_content = res_data["report"]
                        assigned_rating = res_data["rating"]
                        perf_data = res_data["perf"]
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer_content,
                            "rating": assigned_rating
                        })
                        
                        final_styled_report = ExecutiveReportParser.convert_to_html(answer_content, assigned_rating)
                        st.html(final_styled_report)
                        render_performance_metrics(perf_data, ticker_symbol=current_ticker)
                    else:
                        error_text = f"❌ **Pipeline thread execution fault on symbol `{current_ticker}`:** `{res_data['error']}`."
                        st.markdown(error_text)
                        st.session_state.messages.append({"role": "assistant", "content": error_text})
        
        status.update(label="🏁 Concurrent Screening Pipeline Queue Complete", state="complete", expanded=False)
                        
    # -----------------------------------------------------------------
    # 🔒 PERSIST BATCH DATA TO SESSION STATE FOR PERSISTENCE (ADDED)
    # -----------------------------------------------------------------
    st.session_state["latest_batch_summary"] = {
        "count": total_symbols,
        "in_tokens": total_in_tokens,
        "out_tokens": total_out_tokens
    }
    
    st.toast("✅ Parallel Screening Cycle Complete.")
    st.rerun()
