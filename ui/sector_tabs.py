import streamlit as st
import os
import json

class SectorTabRenderer:
    """Handles parsing and structural dropdown layouts for the S&P 500 Symbol matrix."""

    @staticmethod
    def read_sector_file() -> dict:
        """Reads industry sector data directly from the local JSON configuration file using relative paths."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_path = os.path.join(os.path.dirname(current_dir), "sp500_sectors.json")
        package_path = os.path.join(current_dir, "sp500_sectors.json")
        
        target_path = root_path if os.path.exists(root_path) else package_path

        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.sidebar.error(f"⚠️ JSON Format/Syntax Error: {str(e)}")
        else:
            st.sidebar.error(f"⚠️ Target file not found. Place 'sp500_sectors.json' at: {root_path}")
        
        return {"Error Loading File": ["AAPL", "MSFT", "GOOG"]}

    @staticmethod
    def render_symbol_selectors(sector_map: dict):
        """Generates expandable folders containing bulk macro actions and asset selections."""
        for sector_name, tickers in sector_map.items():
            with st.expander(f"📁 {sector_name}", expanded=False):
                key_name = f"sel_{sector_name}"
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Select All {sector_name[:4]}.", key=f"all_{sector_name}"):
                        st.session_state[key_name] = tickers.copy()
                        st.rerun()
                with col2:
                    if st.button(f"Clear {sector_name[:4]}.", key=f"clr_{sector_name}"):
                        st.session_state[key_name] = []
                        st.rerun()
                        
                st.multiselect(
                    "Select assets to queue:", 
                    options=tickers, 
                    key=key_name
                )
