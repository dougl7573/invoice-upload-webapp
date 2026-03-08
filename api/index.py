# Vercel serverless entry. Catch import errors so we can return the real traceback.
import traceback
import json

try:
    from backend.app import app
except Exception as e:
    _tb = traceback.format_exc()
    def app(environ, start_response):
        body = json.dumps({
            "error": "Import failed (api/index.py)",
            "message": str(e),
            "traceback": _tb,
        }, indent=2).encode("utf-8")
        start_response("500 Internal Server Error", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ])
        return [body]
