"""
Airtable client for the web app. Uses env vars for token and base ID.
"""
import os
import requests

TABLE_NAME = "Invoices"


def create_invoice(invoice_data: dict) -> dict | None:
    """Create a new invoice record in Airtable. invoice_data = Airtable fields dict."""
    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not token or not base_id:
        return None
    url = f"https://api.airtable.com/v0/{base_id}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"fields": invoice_data}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None
