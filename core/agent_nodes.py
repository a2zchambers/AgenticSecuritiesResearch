from langchain_core.messages import SystemMessage

class AnalystNodes:
    """Encapsulates the discrete sub-agent inference methods in the evaluation pipeline."""
    
    @staticmethod
    def run_income_analysis(llm_node, directives: str, macro_context: str, metrics: str) -> str:
        """Executes Node 1: Fundamental income flow curves analysis."""
        prompt = (
            "You are an expert Income Statement Analyst node. Core Directives:\n"
            f"{directives}\n\n"
            f"Analyze this context and raw metrics:\n{macro_context}\n{metrics}"
        )
        res = llm_node.invoke([SystemMessage(content=prompt)])
        return res.content

    @staticmethod
    def run_balance_analysis(llm_node, directives: str, income_report: str, metrics: str) -> str:
        """Executes Node 2: Balance Sheet leveraging and liquidity check analysis."""
        prompt = (
            "You are an expert Credit & Balance Sheet Specialist node. Core Directives:\n"
            f"{directives}\n\n"
            "Incorporate findings from the Income Analyst below and evaluate financial health:\n"
            f"Income Report: {income_report}\n\n"
            f"Raw metrics profiles:\n{metrics}"
        )
        res = llm_node.invoke([SystemMessage(content=prompt)])
        return res.content

    @staticmethod
    def run_cash_flow_analysis(llm_node, directives: str, income_report: str, balance_report: str, metrics: str) -> str:
        """Executes Node 3: Deep liquidity and operational Free Cash Flow evaluation."""
        prompt = (
            "You are an expert Cash Flow & Liquidity Operations node. Core Directives:\n"
            f"{directives}\n\n"
            "Evaluate financial durability using the multi-agent context below:\n"
            f"- Income Flow Assessment: {income_report}\n"
            f"- Balance Sheet Health Profile: {balance_report}\n\n"
            f"Raw Financial Metric Matrix Input Data:\n{metrics}"
        )
        res = llm_node.invoke([SystemMessage(content=prompt)])
        return res.content
