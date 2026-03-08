#!/usr/bin/env python3
"""Transform invoice JSON into the format Airtable expects."""


def transform_invoice_for_airtable(invoice):
    """Convert invoice JSON to Airtable record format."""
    line_items_text = "Line Items:\n"
    for item in invoice.get("line_items", []):
        line_items_text += (
            f"- {item['description']}: {item['quantity']} × ${item['unit_price']} = ${item['total']}\n"
        )
    notes = line_items_text.rstrip()
    if invoice.get("notes"):
        notes += f"\n\n{invoice['notes']}"

    return {
        "Invoice Number": invoice["invoice_number"],
        "Vendor": invoice["vendor_name"],
        "Invoice Date": invoice["invoice_date"],
        "Due Date": invoice["due_date"],
        "Amount": invoice["total_amount"],
        "Status": "Received",
        "Notes": notes,
    }
