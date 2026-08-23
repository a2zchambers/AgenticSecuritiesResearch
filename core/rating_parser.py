from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class RatingParser:
    """Handles parsing and crisp classification extraction of agent ratings."""
    
    @staticmethod
    def extract_consensus_rating(model_id: str, base_url: str, report_content: str) -> str:
        """Uses a zero-temperature LLM classification call to extract a strict corporate rating."""
        try:
            llm = ChatOllama(model=model_id, base_url=base_url, temperature=0.0)
            
            system_instruction = (
                "You are an institutional risk compliance parser. Review the provided investment report and classify "
                "the overall directional consensus into exactly ONE of the following precise categories:\n"
                "• STRONG BUY\n• BUY\n• HOLD\n• SELL\n• STRONG SELL\n\n"
                "CRITICAL: You must output ONLY the category name. Do not include introductory text, explanations, notes, or punctuation."
            )
            
            response = llm.invoke([
                SystemMessage(content=system_instruction),
                HumanMessage(content=f"Report Content to evaluate:\n{report_content}")
            ])
            
            cleaned_rating = str(response.content).strip().upper().replace(".", "")
            
            valid_ratings = ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
            for r in valid_ratings:
                if r in cleaned_rating:
                    return r
            return "HOLD"
        except Exception:
            return "HOLD"
