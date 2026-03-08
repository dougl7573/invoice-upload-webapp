#!/usr/bin/env python3
"""
Flask backend for Invoice Upload Web App (Lesson 2.4).
- POST /api/process: accept PDF, return extracted invoice JSON
- POST /api/save: accept invoice JSON, transform and save to Airtable
- GET /: serve frontend
"""
import os
import sys
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# Load .env from backend/ or project root
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Use local pipeline copies (backend is self-contained for Vercel deployment)
from transform_invoice import transform_invoice_for_airtable
from extract_invoice_pdf import extract_invoice_from_pdf

from airtable_client import create_invoice as airtable_create

app = Flask(__name__, static_folder=None)

# Allow frontend (same origin or localhost) to call API
from flask_cors import CORS
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.route("/api/process", methods=["POST"])
def api_process():
    """Accept a PDF file, extract invoice data, return JSON."""
    if "file" not in request.files:
        return jsonify({"error": "No file in request"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        # Save with original filename so extraction can use vendor_from_filename (e.g. invoice-001-acme-corp.pdf)
        with tempfile.TemporaryDirectory() as tmpdir:
            safe_name = os.path.basename(file.filename) or "invoice.pdf"
            tmp_path = os.path.join(tmpdir, safe_name)
            file.save(tmp_path)
            invoice = extract_invoice_from_pdf(tmp_path)
        return jsonify(invoice)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/save", methods=["POST"])
def api_save():
    """Accept invoice JSON (same shape as extracted), transform and save to Airtable."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    if not os.getenv("AIRTABLE_TOKEN") or not os.getenv("AIRTABLE_BASE_ID"):
        return jsonify({"error": "Airtable not configured (AIRTABLE_TOKEN, AIRTABLE_BASE_ID)"}), 500

    try:
        # Transform to Airtable field format (same as Lesson 2.2)
        airtable_data = transform_invoice_for_airtable(data)
        if "Notes" in airtable_data and len(airtable_data.get("Notes", "")) > 100000:
            airtable_data.pop("Notes", None)
        result = airtable_create(airtable_data)
        if result:
            return jsonify({"success": True, "airtable_record_id": result.get("id")})
        return jsonify({"error": "Airtable create failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def frontend_static(path):
    """Serve frontend static files; do not match /api/*."""
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
