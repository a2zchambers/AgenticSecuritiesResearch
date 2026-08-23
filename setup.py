import sys
from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": [
        "streamlit",
        "langchain_core",
        "langchain_ollama",
        "pydantic",
        "pydantic_core",
        "pydantic.deprecated",
        "pydantic.deprecated.decorator",
        "markdown",
        "pyarrow",  
        "tabulate",  # Added to resolve the orchestrator thread worker crash
        "core",
        "ui",
        "storage",
        "data_retrieval",
    ],
    "include_files": [
        "app.py",  
        "sp500_sectors.json",  
        "core/",
        "ui/",
        "storage/",
        "data_retrieval/",
    ],
    "excludes": []
}

setup(
    name="AgenticResearchAnalysts",
    version="1.0",
    description="Streamlit Trading UI Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("run_app.py")], 
)
