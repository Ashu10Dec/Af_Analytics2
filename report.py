# html_report.py

import webbrowser
from datetime import datetime
from pathlib import Path
import html


def generate_html_report(
    question: str,
    answer: str,
    usage_summary: dict,
    output_dir: str = "reports"
):
    Path(output_dir).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qa_report_{timestamp}.html"
    file_path = Path(output_dir) / filename

    def esc(x):
        return html.escape(str(x))

    rows = ""
    for c in usage_summary["calls"]:
        rows += f"""
        <tr>
            <td>{esc(c['stage'])}</td>
            <td>{esc(c['model'])}</td>
            <td>{c['input_tokens']}</td>
            <td>{c['output_tokens']}</td>
            <td>{c['total_tokens']}</td>
            <td>${c['cost_usd']}</td>
        </tr>
        """

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Q&A Report</title>
    <style>
        body {{
            font-family: Segoe UI, Arial, sans-serif;
            margin: 40px;
            background: #f7f9fc;
            color: #222;
        }}
        h1 {{
            color: #2c3e50;
        }}
        .box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        .question {{
            font-size: 18px;
            font-weight: bold;
        }}
        .answer {{
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background: #f0f3f8;
        }}
        .footer {{
            font-size: 12px;
            color: #666;
            margin-top: 20px;
        }}
    </style>
</head>
<body>

<h1>AI Q&A Execution Report</h1>

<div class="box">
    <div class="question">Question</div>
    <p>{esc(question)}</p>
</div>

<div class="box">
    <div class="question">Answer</div>
    <div class="answer">{esc(answer)}</div>
</div>

<div class="box">
    <div class="question">OpenAI API Usage</div>
    <table>
        <thead>
            <tr>
                <th>Stage</th>
                <th>Model</th>
                <th>Input Tokens</th>
                <th>Output Tokens</th>
                <th>Total Tokens</th>
                <th>Cost (USD)</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <p><b>Total Calls:</b> {usage_summary['total_calls']}</p>
    <p><b>Total Tokens:</b> {usage_summary['total_tokens']}</p>
    <p><b>Total Cost:</b> ${usage_summary['total_cost_usd']}</p>
</div>

<div class="footer">
    Generated at {datetime.now().isoformat()}
</div>

</body>
</html>
"""

    file_path.write_text(html_content, encoding="utf-8")

    # Open in default browser
    webbrowser.open(file_path.resolve().as_uri())

    return file_path
