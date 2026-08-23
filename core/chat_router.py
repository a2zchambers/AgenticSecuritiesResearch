import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from core.orchestrator import ExecutionOrchestrator

class StrategicChatRouter:
    """Decouples natural language processing routes into multi-agent pipelines or direct chat streams."""
    def __init__(self):
        self.orchestrator = ExecutionOrchestrator()

    def process_interaction(self, user_input: str, config_payload: dict, response_placeholder) -> tuple:
        """
        Evaluates input content loops. 
        Returns tuple: (output_text_string, rating_string_or_None, performance_metrics_or_None)
        """
        cleaned_input = user_input.upper().strip()
        
        # TRACK 1: RUN EXPLICIT FINANCIAL STATEMENTS COMMITTEE ANALYSIS
        if "RUN RESEARCH" in cleaned_input or "RUN" in cleaned_input or cleaned_input.startswith("ANALYZE"):
            response_placeholder.markdown("⏳ *Spreading custom statement overrides and macro metrics across LangGraph nodes...*")
            
            # FIXED: Unpacks all 4 items from orchestrator.py, including perf_data
            consensus_decision, extracted_rating, model_used, perf_data = self.orchestrator.propagate_langgraph(
                configs=config_payload,
                applied_prompts=st.session_state.prompts
            )
            # Return the metrics back up to app.py
            return consensus_decision, extracted_rating, perf_data
            
        # TRACK 2: GENERAL FINANCIAL AND BROAD KNOWLEDGE ENQUIRY INTERFERENCE
        else:
            response_placeholder.markdown(f"⏳ *Routing query to general intelligence model node **{config_payload['model_id']}**...*")
            ollama_base_url = config_payload["endpoint"].strip().replace("/v1", "")
            general_llm = ChatOllama(model=config_payload["model_id"], base_url=ollama_base_url, temperature=0.3)
            
            system_context = (
                "You are an expert institutional investment advisor representing A2Z Chambers Inc. "
                "Provide a comprehensive, high-density, accurate answer to the user's question. "
                "Use markdown syntax, bullets, or headers where appropriate to keep it readable."
            )
            
            messages_payload = [
                SystemMessage(content=system_context),
                HumanMessage(content=user_input)
            ]
            
            model_reply = general_llm.invoke(messages_payload)
            # General talk queries return None for metrics
            return model_reply.content, None, None
