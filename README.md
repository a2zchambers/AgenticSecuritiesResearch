# 🤖 Agentic Securities Research

[![Python Version](https://img.shields.io)](https://python.org)
[![AI Engine](https://img.shields.io)](https://ollama.com/)
[![License](https://img.shields.io)](LICENSE)

An autonomous, multi-agent AI framework built to conduct localized security analysis, aggregate financial data, and backtest sector-specific algorithmic trading strategies. 

By executing entirely on **local Ollama models**, this project ensures complete data privacy—your financial research queries, API data, and database strategies never leave your hardware.

---

## ✨ Key Features

* **Local AI Execution:** Complete inference privacy powered by local LLMs via `Ollama`.
* **Multi-Agent Coordination:** Orchestrated analysis workflows split among specialized research and strategy sub-agents.
* **Automated Data Retrieval:** Pulls live market information and maps S&P 500 sectors dynamically.
* **Local Strategy Storage:** Saves backtesting results securely to a local SQLite database ecosystem (`trading_results.db`).
* **Interactive UI Dashboard:** Review and visualize financial insights directly inside a localized application window.

---

## 📂 Project Architecture

```text
📦 AgenticSecuritiesResearch
 ┣ 📂 agenticresearchanalysts # Core multi-agent reasoning logic
 ┣ 📂 core                    # Shared logic, configurations, and global initializers
 ┣ 📂 data_retrieval          # Market scrapers and financial API connections
 ┣ 📂 storage                 # DB schemas and local data handlers
 ┣ 📂 ui                      # Front-end dashboard and visualization assets
 ┣ 📜 app.py                  # Main backend server interface
 ┣ 📜 sp500_sectors.json      # Structured dictionary mapping market sectors
 ┣ 📜 trading_results.db      # Local SQLite database for model backtests
 ┣ 📜 requirements.txt        # Third-party package dependencies
 ┗ 📜 .gitignore              # Local build and environment exclusions
```

---

## 🛠️ Getting Started

### 1. Prerequisites
* **Python 3.9+** installed on your system.
* **Ollama** installed and running locally. 
  * Download it from the [Official Ollama Website](https://ollama.com/).

### 2. Pull Your Local AI Models
Ensure your local Ollama server is running, then open a terminal and download your preferred reasoning LLM (e.g., Llama 3, Mistral, or Phi-3):

```bash
# Start your local server if it isn't running automatically
ollama serve

# Pull your preferred model (example using muse-glimmer:30b-mlx) for mac
ollama pull muse-glimmer:30b-mlx

ollama pull muse-glimmer:30b # for windows
```
### 3. Installation
Clone the repository and install the project along with its required dependencies:

```bash
# Clone the repository
git clone https://github.com
cd AgenticSecuritiesResearch

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
pip install -e .
```

### 4. Running the Application
Launch the autonomous research system by running the entry point script:
```bash
streamlit run app.py
```
or
```bash
python -m streamlit run app.py
```

---

## ⚙️ Configuration
Modify your model selections or local API parameters inside the `core/` configuration directory to adjust which local Ollama model handles individual analytics assignments.

## 📄 License
This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
