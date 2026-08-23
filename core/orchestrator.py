import traceback
import time
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from data_retrieval.data_fetcher import FundamentalDataFetcher

# FIXED: Points directly to the newly isolated storage folder layer
from storage.sqlite_manager import DatabaseManager

# Import decoupled relative package modules using dot-notation
from core.rating_parser import RatingParser
from core.agent_nodes import AnalystNodes
from ui.telemetry import TelemetryTracker
from data_retrieval.sector_loader import SectorLoader

class ExecutionOrchestrator:
    """Manages prompt baseline profiles and orchestrates localized multi-agent consensus logic."""
    
    def __init__(self, db_path: str = "trading_results.db"):
        # FIXED: Instantiates the decoupled persistence class manager safely
        self.db_manager = DatabaseManager(db_path)
        self.sector_lookup = SectorLoader.load_sector_lookup()
        
    @property
    def db_path(self) -> str:
        return self.db_manager.db_path

    @property
    def default_prompts(self) -> dict:
        return {
            "income_statement": (
                "Evaluate revenue growth curves, operating profit margins, net income durability, "
                "and cost of goods sold (COGS) structures over successive quarters."
            ),
            "balance_sheet": (
                "Examine current liquidity positions, long-term debt leveraging risks, total asset "
                "turnover efficiency, and shifts in retained equity balances."
            ),
            "cash_flow": (
                "Analyze operating cash flow generation, capital expenditure (CapEx) trends, financing "
                "cash adjustments, and net changes in Free Cash Flow (FCF) margins."
            )
        }

    def propagate_langgraph(self, configs: dict, applied_prompts: dict) -> tuple:
        """
        Chains isolated agent sub-nodes (Income, Balance, Cash Flow) and writes outputs to the database layer.
        
        RETURNS:
            tuple: (final_report_text, extracted_rating_string, active_model_used_string, performance_metrics_dict, internal_logs_list)
        """
        performance_metrics = {"Input Tokens": 0, "Output Tokens": 0}
        internal_logs = ["[System Log] Initializing standalone analytical matrix..."]
        global_start_time = time.time()
        
        try:
            target_ticker = configs["ticker"].strip().upper()
            assigned_sector = self.sector_lookup.get(target_ticker, "UNKNOWN")
            
            raw_url = configs["endpoint"].strip()
            if raw_url.endswith("/"): raw_url = raw_url[:-1]
            ollama_base_url = raw_url.replace("/v1", "")

            internal_logs.append(f"[System Log] Ingesting quarterly sheets via FundamentalDataFetcher for {target_ticker}...")
            
            fetch_start = time.time()
            statement_payload = FundamentalDataFetcher.fetch_quarterly_sheets(configs["ticker"])
            performance_metrics["Data Fetch Time"] = round(time.time() - fetch_start, 2)
            
            macro_context_injection = (
                f"\n[LOCAL FUNDAMENTAL TRADING DESK CONSTRAINTS]\n"
                f"- Targeted Asset Symbol: {target_ticker}\n"
                f"- Asset GICS Sector Classification: {assigned_sector}\n"
                f"- Crude Oil Pricing Assumptions: ${configs['oil_price']}/bbl\n"
                f"- Target Federal Funds Rate: {configs['interest_rate']}%\n"
                f"- Macro Economic Regime Track: {configs['macro_regime']}\n"
            )
            
            llm_node = ChatOllama(model=configs["model_id"], base_url=ollama_base_url, temperature=0.0)
            
            # --- NODE 1: INCOME STATEMENT ANALYSIS ---
            internal_logs.append("[System Log] Invoking Income Statement Node inference...")
            node1_start = time.time()
            prompt_income = (
                "You are an expert Income Statement Analyst node. Core Directives:\n"
                f"{applied_prompts['income_statement']}\n\n"
                f"Analyze this context and raw metrics:\n{macro_context_injection}\n{statement_payload}"
            )
            res_income = llm_node.invoke([SystemMessage(content=prompt_income)])
            res_income_content = res_income.content
            performance_metrics["Income Analyst Node"] = round(time.time() - node1_start, 2)
            TelemetryTracker.extract_token_counts(res_income, prompt_income, performance_metrics)
            
            # --- NODE 2: BALANCE SHEET ANALYSIS ---
            internal_logs.append("[System Log] Invoking Balance Sheet Node inference...")
            node2_start = time.time()
            prompt_balance = (
                "You are an expert Credit & Balance Sheet Specialist node. Core Directives:\n"
                f"{applied_prompts['balance_sheet']}\n\n"
                "Incorporate findings from the Income Analyst below and evaluate financial health:\n"
                f"Income Report: {res_income_content}\n\n"
                f"Raw metrics profiles:\n{statement_payload}"
            )
            res_balance = llm_node.invoke([SystemMessage(content=prompt_balance)])
            res_balance_content = res_balance.content
            performance_metrics["Balance Analyst Node"] = round(time.time() - node2_start, 2)
            TelemetryTracker.extract_token_counts(res_balance, prompt_balance, performance_metrics)

            # --- NODE 3: CASH FLOW ANALYSIS ---
            internal_logs.append("[System Log] Invoking Cash Flow Node inference...")
            node3_start = time.time()
            prompt_cf = (
                "You are an expert Cash Flow & Liquidity Operations node. Core Directives:\n"
                f"{applied_prompts['cash_flow']}\n\n"
                "Evaluate financial durability using the multi-agent context below:\n"
                f"- Income Flow Assessment: {res_income_content}\n"
                f"- Balance Sheet Health Profile: {res_balance_content}\n\n"
                f"Raw Financial Metric Matrix Input Data:\n{statement_payload}"
            )
            res_cf = llm_node.invoke([SystemMessage(content=prompt_cf)])
            res_cash_flow_content = res_cf.content
            performance_metrics["Cash Flow Node"] = round(time.time() - node3_start, 2)
            TelemetryTracker.extract_token_counts(res_cf, prompt_cf, performance_metrics)

            # --- NODE 4: CONSENSUS DIRECTOR ---
            internal_logs.append("[System Log] Generating consolidated final committee report...")
            node4_start = time.time()
            final_committee_system_prompt = (
                "You are the Committee Consensus Director representing A2Z Chambers Inc.\n"
                "Synthesize sub-analyst node findings into a single cohesive, high-density investment report.\n"
                "Ensure your summary integrates observations from all three disciplines: Income Statement, Balance Sheet, and Cash Flow.\n"
                "Organize your report with clear sections and end with an easy-to-read Markdown summary table. "
                "Ensure you make an explicit terminal action recommendation call (Strong Buy, Buy, Hold, Sell, Strong Sell) based on data evidence."
            )
            final_human_input = (
                f"Please compile the final consensus evaluation report for {target_ticker}.\n"
                f"• Income Analyst Report: {res_income_content}\n\n"
                f"• Balance Sheet Analyst Report: {res_balance_content}\n\n"
                f"• Cash Flow Analyst Report: {res_cash_flow_content}\n\n"
                f"• Macro parameters applied: {macro_context_injection}"
            )
            final_response = llm_node.invoke([
                SystemMessage(content=final_committee_system_prompt),
                HumanMessage(content=final_human_input)
            ])
            report_body = final_response.content
            performance_metrics["Consensus Director Node"] = round(time.time() - node4_start, 2)
            TelemetryTracker.extract_token_counts(final_response, final_committee_system_prompt + final_human_input, performance_metrics)
            
            # --- EXTRACT RECOMMENDATION RATING ---
            rating_start = time.time()
            extracted_rating = RatingParser.extract_consensus_rating(
                model_id=configs["model_id"],
                base_url=ollama_base_url,
                report_content=report_body
            )
            internal_logs.append(f"[System Log] Extracted committee consensus action vector: {extracted_rating}")

            # Commit the final analysis parameters straight into SQLite persistence layers
            self.db_manager.save_run_result(
                rating=extracted_rating,
                ticker=target_ticker,
                sector=assigned_sector,
                reason=report_body,
                model_used=configs["model_id"]
            )
            
            performance_metrics["Total Cycle Time"] = round(time.time() - global_start_time, 2)
            return report_body, extracted_rating, configs["model_id"], performance_metrics, internal_logs

        except Exception as orchestrator_fault:
            performance_metrics["Total Cycle Time"] = round(time.time() - global_start_time, 2)
            fault_trace = traceback.format_exc()
            error_msg = f"Orchestrator pipeline failed inside thread worker context: {str(orchestrator_fault)}"
            return error_msg, "HOLD", configs.get("model_id", "UNKNOWN"), performance_metrics, internal_logs + [f"[Critical Error] {fault_trace}"]
