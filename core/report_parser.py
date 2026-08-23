import re
import markdown

class ExecutiveReportParser:
    """Compiles raw text or markdown payloads into styled HTML canvas templates for A2Z Chambers Inc."""
    
    @staticmethod
    def convert_to_html(markdown_text: str, rating_str: str = None) -> str:
        raw_content = markdown_text
        
        # Strip code block wrappers if appended by fallback logs
        if "```text" in raw_content:
            raw_content = raw_content.replace("```text", "").replace("```", "")
        if "Fallback Interface Route Triggered" in raw_content:
            raw_content = raw_content.split("]**\n\n")[-1]

        # Generate structural badge content header matrices
        if rating_str:
            badge_colors = {
                "STRONG BUY": {"bg": "#dcfce7", "text": "#15803d", "border": "#bbf7d0"},
                "BUY": {"bg": "#e0f2fe", "text": "#0369a1", "border": "#bae6fd"},
                "HOLD": {"bg": "#fef3c7", "text": "#b45309", "border": "#fde68a"},
                "SELL": {"bg": "#ffedd5", "text": "#c2410c", "border": "#fed7aa"},
                "STRONG SELL": {"bg": "#fee2e2", "text": "#b91c1c", "border": "#fecaca"}
            }
            color = badge_colors.get(rating_str, {"bg": "#f1f5f9", "text": "#475569", "border": "#cbd5e1"})

            badge_html = f"""
            <div class="rating-badge-container">
                <span class="rating-label">CONSENSUS ACTION RATING:</span>
                <span class="rating-badge">{rating_str}</span>
            </div>
            """
        else:
            badge_html = """
            <div class="rating-badge-container">
                <span class="rating-label">GENERAL INTELLIGENCE NODE ANALYSIS</span>
            </div>
            """

        # Regex Markdown Table Parser extraction grid loop
        table_pattern = r"(\|.*\|\n\|[\s\-\|]*\|\n(?:\|.*\|\n?)*)"
        match = re.search(table_pattern, raw_content)
        
        table_html = ""
        if match:
            raw_table = match.group(1)
            raw_content = raw_content.replace(raw_table, "<!-- TABLE_SLOT -->")
            
            lines = [line.strip() for line in raw_table.strip().split("\n") if line.strip()]
            if len(lines) >= 3:
                headers = [h.strip() for h in lines[0].split("|")[1:-1]]
                rows = []
                for row in lines[2:]:
                    rows.append([cell.strip() for cell in row.split("|")[1:-1]])
                    
                table_html = "<div class='table-container'><table>"
                table_html += "<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
                for r in rows:
                    if len(r) == len(headers):
                        table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                table_html += "</tbody></table></div>"

        # Standard clean markdown element evaluation
        compiled_html = markdown.markdown(raw_content, extensions=['tables', 'fenced_code'])

        if "<!-- TABLE_SLOT -->" in compiled_html:
            compiled_html = compiled_html.replace("<!-- TABLE_SLOT -->", table_html)
        else:
            compiled_html += table_html

        # CSS Corporate Layout Template block encapsulation
        return f"""
        <style>
            .executive-report-body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #ffffff;
                color: #1e293b;
                padding: 30px;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
                line-height: 1.7;
                margin-top: 15px;
            }}
            .rating-badge-container {{
                display: flex;
                align-items: center;
                background-color: #f8fafc;
                padding: 12px 20px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                margin-bottom: 25px;
            }}
            .rating-label {{
                font-size: 13px;
                font-weight: 700;
                color: #475569;
                letter-spacing: 0.05em;
                margin-right: 15px;
            }}
            .rating-badge {{
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 0.03em;
                background-color: {color['bg'] if rating_str else '#f1f5f9'};
                color: {color['text'] if rating_str else '#475569'};
                border: 1px solid {color['border'] if rating_str else '#cbd5e1'};
                padding: 6px 16px;
                border-radius: 6px;
                box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);
            }}
            .executive-report-body h1, .executive-report-body h2, .executive-report-body h3 {{
                color: #1e3a8a;
                border-bottom: 2px solid #3b82f6;
                padding-bottom: 6px;
                margin-top: 25px;
                margin-bottom: 12px;
                font-weight: 600;
                letter-spacing: -0.02em;
            }}
            .executive-report-body h1:first-of-type, .executive-report-body h2:first-of-type, .executive-report-body h3:first-of-type {{
                margin-top: 0;
                font-size: 24px;
                border-bottom: 3px solid #1e3a8a;
                color: #1e3a8a;
            }}
            .executive-report-body p {{
                margin-bottom: 15px;
                color: #334155;
            }}
            .executive-report-body ul, .executive-report-body ol {{
                margin-top: 5px;
                margin-bottom: 20px;
                padding-left: 25px;
            }}
            .executive-report-body li {{
                margin-bottom: 8px;
                color: #334155;
            }}
            .executive-report-body li strong {{
                color: #0f172a;
                font-weight: 600;
            }}
            .table-container {{
                overflow-x: auto;
                margin: 25px 0;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }}
            .executive-report-body table {{
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-size: 14px;
            }}
            .executive-report-body th {{
                background-color: #1e3a8a;
                color: #ffffff;
                font-weight: 600;
                padding: 12px 16px;
            }}
            .executive-report-body td {{
                padding: 12px 16px;
                border-bottom: 1px solid #e2e8f0;
                color: #334155;
            }}
            .executive-report-body tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            .executive-report-body tr:hover {{
                background-color: #f1f5f9;
            }}
        </style>
        <div class='executive-report-body'>
            {badge_html}
            {compiled_html}
        </div>
        """
