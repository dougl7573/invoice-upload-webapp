#!/usr/bin/env python3
"""
Flask backend for Invoice Upload Web App (Lesson 2.4).
- POST /api/process: accept PDF, return extracted invoice JSON
- POST /api/save: accept invoice JSON, transform and save to Airtable
- GET /api/health: health check (for Vercel serverless)
- GET /: serve frontend (or rely on Vercel public/ for static)
"""
import os
import sys
import tempfile
import traceback

try:
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass

from flask import Flask, jsonify, request, send_from_directory

# Defer heavy imports to avoid serverless cold-start crash; import inside route handlers
_app_error = None
try:
    from flask_cors import CORS
    app = Flask(__name__, static_folder=None)
    CORS(app)

    _BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIR = os.path.join(_BACKEND_DIR, "..", "frontend")
    if not os.path.isdir(FRONTEND_DIR):
        FRONTEND_DIR = os.path.join(os.getcwd(), "public")

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return jsonify({"ok": True})

    @app.route("/api/process", methods=["POST"])
    def api_process():
        if "file" not in request.files:
            return jsonify({"error": "No file in request"}), 400
        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "File must be a PDF"}), 400
        try:
            from extract_invoice_pdf import extract_invoice_from_pdf
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
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON body"}), 400
        if not os.getenv("AIRTABLE_TOKEN") or not os.getenv("AIRTABLE_BASE_ID"):
            return jsonify({"error": "Airtable not configured (AIRTABLE_TOKEN, AIRTABLE_BASE_ID)"}), 500
        try:
            from transform_invoice import transform_invoice_for_airtable
            from airtable_client import create_invoice as airtable_create
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
        if not os.path.isdir(FRONTEND_DIR):
            return jsonify({"error": "Frontend not found", "FRONTEND_DIR": FRONTEND_DIR}), 404
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:path>")
    def frontend_static(path):
        if path.startswith("api/"):
            return jsonify({"error": "Not found"}), 404
        if not os.path.isdir(FRONTEND_DIR):
            return jsonify({"error": "Not found"}), 404
        return send_from_directory(FRONTEND_DIR, path)

except Exception as e:
    _app_error = e
    _app_traceback = traceback.format_exc()
    app = Flask(__name__)
    app.config["APPLICATION_ERROR"] = str(e)
    app.config["APPLICATION_TRACEBACK"] = _app_traceback

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def _error_handler(path):
        return jsonify({
            "error": "App failed to start",
            "message": str(_app_error),
            "traceback": _app_traceback,
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
