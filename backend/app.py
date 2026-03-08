#!/usr/bin/env python3
"""
Flask backend for Invoice Upload Web App (Lesson 2.4).
All imports and app creation wrapped in try/except so Vercel crashes return the real error.
"""
import json
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

_app_error = None
_app_traceback = None

try:
    from flask import Flask, jsonify, request, send_from_directory
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
            from backend.extract_invoice_pdf import extract_invoice_from_pdf
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
            from backend.transform_invoice import transform_invoice_for_airtable
            from backend.airtable_client import create_invoice as airtable_create
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

    # Fallback: minimal WSGI app that returns the error (no Flask dependency)
    def app(environ, start_response):
        body = json.dumps({
            "error": "App failed to start",
            "message": str(_app_error),
            "traceback": _app_traceback,
        }, indent=2).encode("utf-8")
        start_response("500 Internal Server Error", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if hasattr(app, "run"):
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        from wsgiref.simple_server import make_server
        make_server("0.0.0.0", port, app).serve_forever()
