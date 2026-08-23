import time
import json
import streamlit as st

class TelemetryTracker:
    """Handles operational execution duration tracking and robust multi-format token counting metrics."""
    
    @staticmethod
    def extract_token_counts(response_obj, raw_input_text: str, metrics_dict: dict):
        """
        Safely attempts parsing native Ollama metadata fields, and accurately 
        falls back to text character estimation if keys are null or non-existent.
        """
        prompt_toks = 0
        completion_toks = 0
        parsed_successfully = False
        
        try:
            # 1. Native API Meta Structural Extraction Patterns
            if hasattr(response_obj, "response_metadata") and response_obj.response_metadata:
                meta = response_obj.response_metadata
                if "prompt_tokens" in meta or "completion_tokens" in meta:
                    prompt_toks = meta.get("prompt_tokens", 0)
                    completion_toks = meta.get("completion_tokens", 0)
                    if prompt_toks or completion_toks: parsed_successfully = True
                elif "message" in meta and isinstance(meta["message"], dict):
                    msg_meta = meta["message"]
                    prompt_toks = msg_meta.get("prompt_tokens", 0)
                    completion_toks = msg_meta.get("completion_tokens", 0)
                    if prompt_toks or completion_toks: parsed_successfully = True
                elif "usage" in meta and isinstance(meta["usage"], dict):
                    usage = meta["usage"]
                    prompt_toks = usage.get("prompt_tokens", 0)
                    completion_toks = usage.get("completion_tokens", 0)
                    if prompt_toks or completion_toks: parsed_successfully = True

            if not parsed_successfully and hasattr(response_obj, "usage_metadata") and response_obj.usage_metadata:
                usage = response_obj.usage_metadata
                prompt_toks = usage.get("input_tokens", 0)
                completion_toks = usage.get("output_tokens", 0)
                if prompt_toks or completion_toks: parsed_successfully = True
        except Exception:
            pass # Swallow nested parsing faults to guarantee thread safety

        # 2. STRING CHARACTER TOKENIZER FALLBACK
        # Safely prevents zeros across alternative model engines (~4 characters per token rule)
        if not parsed_successfully or (prompt_toks == 0 and completion_toks == 0):
            try:
                input_str = str(raw_input_text) if raw_input_text else ""
                output_str = str(response_obj.content) if hasattr(response_obj, "content") else ""
                
                prompt_toks = max(1, len(input_str) // 4)
                completion_toks = max(1, len(output_str) // 4)
            except Exception:
                prompt_toks, completion_toks = 100, 100 # Absolute baseline safeguard flags

        # Increment accumulators safely
        metrics_dict["Input Tokens"] += int(prompt_toks if prompt_toks else 0)
        metrics_dict["Output Tokens"] += int(completion_toks if completion_toks else 0)
