import math
import os
import re
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

import database
from fraud_detector import VALID_TYPES, calculate_risk


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(DATABASE=os.environ.get("FINCHECK_DATABASE", os.path.join(app.root_path, "instance", "transactions.sqlite3")))
    if config:
        app.config.update(config)
    database.init_db(app.config["DATABASE"])

    def error(message, status):
        return jsonify(error=message), status

    def payload():
        if not request.is_json:
            raise ValueError("Content-Type must be application/json")
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        required = {"transaction_id", "amount", "location", "transaction_type"}
        missing = sorted(required - data.keys())
        if missing:
            raise ValueError("Missing required fields: " + ", ".join(missing))
        tid, loc, kind, amount = data["transaction_id"], data["location"], data["transaction_type"], data["amount"]
        if not isinstance(tid, str) or not tid.strip() or len(tid.strip()) > 64 or not re.fullmatch(r"[A-Za-z0-9_-]+", tid.strip()):
            raise ValueError("transaction_id must be 1-64 letters, numbers, underscores, or hyphens")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount <= 0:
            raise ValueError("amount must be a finite number greater than zero")
        if not isinstance(loc, str) or not loc.strip() or len(loc.strip()) > 80:
            raise ValueError("location must be a non-empty string of at most 80 characters")
        if not isinstance(kind, str) or kind not in VALID_TYPES:
            raise ValueError("transaction_type must be one of: " + ", ".join(sorted(VALID_TYPES)))
        return tid.strip(), float(amount), loc.strip(), kind

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/history")
    def history_page():
        return render_template("history.html")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", service="financial-fraud-detection")

    @app.post("/api/analyze")
    def analyze():
        try:
            tid, amount, location, kind = payload()
        except ValueError as exc:
            return error(str(exc), 400)
        score, status = calculate_risk(amount, location, kind)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            with database.connect(app.config["DATABASE"]) as conn:
                conn.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)", (tid, amount, location, kind, score, status, created))
        except sqlite3.IntegrityError:
            return error("transaction_id already exists", 409)
        return jsonify(transaction_id=tid, risk_score=score, status=status, created_at=created), 201

    @app.get("/api/transactions")
    def list_transactions():
        with database.connect(app.config["DATABASE"]) as conn:
            rows = conn.execute("SELECT * FROM transactions ORDER BY created_at DESC, transaction_id").fetchall()
        return jsonify(transactions=[dict(row) for row in rows])

    @app.get("/api/transactions/<transaction_id>")
    def get_transaction(transaction_id):
        with database.connect(app.config["DATABASE"]) as conn:
            row = conn.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)).fetchone()
        if row is None:
            return error("transaction not found", 404)
        return jsonify(dict(row))

    @app.delete("/api/transactions/<transaction_id>")
    def delete_transaction(transaction_id):
        with database.connect(app.config["DATABASE"]) as conn:
            cur = conn.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
        if not cur.rowcount:
            return error("transaction not found", 404)
        return jsonify(message="transaction deleted", transaction_id=transaction_id)

    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith("/api/"):
            return error("resource not found", 404)
        return "Not found", 404

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
