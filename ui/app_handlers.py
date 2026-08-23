import streamlit as st

# FIXED: Redirected old invalid path to point directly to your new ui package subfolder
from ui.history_dialog import show_history_modal

def handle_maintenance_triggers(config_payload: dict, orchestrator):
    """Intercepts utility tab button clicks to display modal overlays or flush workspaces."""
    if config_payload.get("trigger_history_modal"):
        show_history_modal(orchestrator)

    if config_payload.get("trigger_wipe_chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Local desk online. Fundamental prompt modules loaded. How shall we direct the analyst team?"}
        ]
        st.session_state["latest_batch_summary"] = None  
        st.toast("🗑️ Chat workspace wiped successfully.")
        st.rerun()
