import streamlit as st

def inject_corporate_styles():
    """Injects a locked, non-blocking top banner layout for branding consistency."""
    st.markdown(
        """
        <style>
        /* Pin corporate branding permanently at the absolute top layer of the DOM */
        .fixed-header-banner {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            background-color: #0f172a; /* Corporate deep slate */
            color: #f8fafc;
            padding: 12px 24px;
            z-index: 999999; /* Forces banner above all scrolling content layers */
            border-bottom: 2px solid #1e293b;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        
        .fixed-header-banner h2 {
            margin: 0 !important;
            padding: 0 !important;
            color: #f8fafc !important;
            font-size: 20px !important;
        }
        
        .fixed-header-banner p {
            margin: 0 !important;
            padding: 0 !important;
            color: #94a3b8 !important;
            font-size: 12px !important;
        }

        /* FIXED: Pushes main application canvas blocks down so tabs never get covered */
        .stApp {
            margin-top: 55px !important;
        }

        /* Adjust base top container padding margins */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
        
        /* Scannable evaluation badges layout configuration */
        .report-rating-badge {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: #1e293b;
            color: #f8fafc;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
