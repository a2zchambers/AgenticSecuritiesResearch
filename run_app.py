import os
import sys
import streamlit.web.cli as stcli

# Explicitly force cx_Freeze to see these nested streamlit modules
import streamlit.runtime.scriptrunner_utils.script_run_context

def resolve_path(path):
    # If running inside a frozen cx_Freeze executable
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(base_path, path))

if __name__ == "__main__":
    # Point the internal CLI directly at your main Streamlit app file
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--global.developmentMode=false"
    ]
    sys.exit(stcli.main())
