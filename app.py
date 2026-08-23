import streamlit as st

# MUST BE THE VERY FIRST STREAMLIT DIRECTIVE CALL IN THE FILE
st.set_page_config(
    page_title="A2Z Chambers Inc. | Institutional Workspace",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Package paths and structural helper modules
from ui.ui_components import TradingUI
from core.orchestrator import ExecutionOrchestrator
from core.chat_router import StrategicChatRouter
from ui.styles import inject_corporate_styles

# Coupled visual layout sub-modules
from ui.app_handlers import handle_maintenance_triggers
from ui.portfolio_dashboard import render_portfolio_dashboard
from ui.chat_renderer import render_batch_summary

# Instantiate core engines
ui = TradingUI()
orchestrator = ExecutionOrchestrator()
router = StrategicChatRouter()

# Force initialize variables at the absolute top before ANY rendering takes place
ui.initialize_session_state(default_prompts=orchestrator.default_prompts)

# Inject corporate styles and sidebar configurations
inject_corporate_styles()
config_payload = ui.render_sidebar()

# Handle Maintenance Modal Actions
handle_maintenance_triggers(config_payload, orchestrator)

# Intercept trade intent state sent from the history modal to launch the trade terminal safely from the main canvas context
if "active_trade_intent" in st.session_state and st.session_state["active_trade_intent"]:
    from ui.alpaca_dialog import show_order_placement_modal
    trade_info = st.session_state["active_trade_intent"]
    st.session_state["active_trade_intent"] = None
    show_order_placement_modal(ticker=trade_info["ticker"], consensus_rating=trade_info["rating"])

# Pinned header banner block that stays on screen while scrolling down
st.markdown(
    """
    <div class="fixed-header-banner">
        <h2>🏛️ A2Z Chambers Inc.</h2>
        <p>Institutional Investment Screening Workspace Portal</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Render the workspace tabs and pass runtime references into the playground engine scope 
ui.render_fundamental_playground(config_payload, orchestrator, router)

# FIXED: Completely removed 'render_portfolio_dashboard(config_payload)' from this line.
# This eliminates the bottom-of-page balance summary duplicate rendering entirely.

# Injects the persistent batch execution toast bar if loaded
render_batch_summary()
