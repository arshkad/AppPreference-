"""
this is app.py
Flask web application — runs the Python data pipeline and serves
all chart data via a JSON API consumed by the frontend.
"""

from flask import Flask, render_template, jsonify
from data_engine import run_pipeline

app = Flask(__name__)

# Run pipeline once at startup (cache result)
_pipeline_data = None

def get_data():
    global _pipeline_data
    if _pipeline_data is None:
        _pipeline_data = run_pipeline()
    return _pipeline_data

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Render the dashboard shell."""
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    """Return full pipeline output as JSON."""
    return jsonify(get_data())


@app.route("/api/refresh")
def api_refresh():
    """Re-run the pipeline with a new random seed (demo purposes)."""
    global _pipeline_data
    _pipeline_data = None
    return jsonify({"status": "refreshed"})


if __name__ == "__main__":
    print("Starting DS Research Dashboard…")
    print("Open http://localhost:5000 in your browser.")
    app.run(debug=True, port=5000)