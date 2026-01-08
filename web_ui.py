import json
import os
import threading
import webbrowser
from flask import Flask, request, render_template_string

def start_web_app(ask_question_fn, usage_tracker):
    app = Flask(__name__)

    # --- History Configuration ---
    HISTORY_FILE = "question_history.json"
    
    # Load history from file on startup
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                question_history = json.load(f)
        except Exception:
            question_history = []
    else:
        question_history = []

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>JSON Analytics Q&A</title>
        <style>
            body {
                font-family: Segoe UI, Arial;
                background: #f4f6fa;
                margin: 0;
                padding: 0;
                display: flex;
            }

            .sidebar {
                width: 260px;
                background: #0b1f3b;
                color: white;
                padding: 20px;
                height: 100vh;
            }

            .sidebar h3 {
                margin-top: 0;
                color: #ffb347;
            }

            .sidebar a {
                display: block;
                color: #dbe6ff;
                text-decoration: none;
                margin-bottom: 10px;
                font-size: 14px;
            }

            .sidebar a:hover {
                color: #ffb347;
            }

            .content {
                flex: 1;
                padding: 40px;
            }

            .box {
                background: white;
                padding: 25px;
                border-radius: 8px;
                max-width: 900px;
                margin: auto;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            }

            h2 {
                color: #0b1f3b;
            }

            textarea {
                width: 100%;
                height: 90px;
                font-size: 16px;
                padding: 10px;
            }

            button {
                margin-top: 10px;
                padding: 10px 18px;
                font-size: 15px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
            }

            .ask-btn {
                background: #0b1f3b;
                color: white;
            }

            .clear-btn {
                background: #ffb347;
                color: #222;
                margin-left: 10px;
                text-decoration: none;
                padding: 10px 18px;
                border-radius: 4px;
            }

            /* --- UI FIX: Reduced Spacing --- */
            .answer {
                margin-top: 5px;   /* Reduced from 15px */
                white-space: pre-wrap;
            }

            .answer h3 {
                margin-top: 0;     /* Removed default browser margin */
                margin-bottom: 5px;
                color: #0b1f3b;
            }

            .usage {
                margin-top: 20px;
                font-size: 14px;
                background: #f7f9fc;
                padding: 10px;
                border-radius: 6px;
            }
        </style>
    </head>
    <body>

    <div class="sidebar">
        <h3>Previous Questions</h3>
        {% for q in history %}
            <a href="/?q={{ q }}">{{ q }}</a>
        {% else %}
            <p style="font-size:13px;color:#aaa;">No questions yet</p>
        {% endfor %}
    </div>

    <div class="content">
        <div class="box">
            <h2>JSON Analytics – Ask a Question</h2>

            <form method="post">
                <textarea name="question" placeholder="Ask your question...">{{ question }}</textarea><br>
                <button class="ask-btn" type="submit">Ask</button>
                <a href="/" class="clear-btn">Clear</a>
            </form>

            {% if answer %}
            <div class="answer">
                <h3>Answer</h3>
                <p>{{ answer }}</p>
            </div>

            <div class="usage">
                <b>API Usage</b>
                <pre>{{ usage }}</pre>
            </div>
            {% endif %}
        </div>
    </div>

    </body>
    </html>
    """

    @app.route("/", methods=["GET", "POST"])
    def home():
        nonlocal question_history
        answer = None
        usage_text = ""
        question = ""

        selected_question = request.args.get("q")

        if selected_question:
            question = selected_question
            answer = ask_question_fn(question)

        elif request.method == "POST":
            question = request.form.get("question", "").strip()
            if question:
                # Remove if exists (to bump to top), then append
                if question in question_history:
                    question_history.remove(question)
                question_history.append(question)
                
                # Keep only the last 2 items
                if len(question_history) > 10:
                    question_history = question_history[-10:]
                
                # Save to file
                try:
                    with open(HISTORY_FILE, "w") as f:
                        json.dump(question_history, f)
                except Exception as e:
                    print(f"Error saving history: {e}")

                answer = ask_question_fn(question)

        if answer:
            usage = usage_tracker.summary()
            usage_text = (
                f"Total calls: {usage['total_calls']}\n"
                f"Total tokens: {usage['total_tokens']}\n"
                f"Total cost (USD): ${usage['total_cost_usd']}"
            )

        return render_template_string(
            HTML_TEMPLATE,
            question=question,
            answer=answer,
            usage=usage_text,
            history=reversed(question_history)
        )

    def open_browser():
        webbrowser.open("http://127.0.0.1:8080")

    threading.Timer(1, open_browser).start()
    app.run(host="127.0.0.1", port=8080, debug=False)
