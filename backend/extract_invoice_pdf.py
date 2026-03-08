#!/usr/bin/env python3
"""
Extract invoice data from a PDF (used by webapp backend).
Uses pdfplumber for text and table extraction.
"""
import re
import sys


def extract_invoice_from_pdf(pdf_path: str) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        all_tables = []
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
            tables = page.extract_tables()
            if tables:
                all_tables.extend(tables)

    invoice_number = _find_pattern(
        full_text,
        r"(?:invoice\s*#?\s*[:\s]*|inv\.?\s*[#:]\s*)(?:</?\w+>)*\s*([A-Za-z0-9\-]{2,})",
        "invoice_number",
    )
    if not invoice_number or not _looks_like_invoice_number(invoice_number):
        invoice_number = _find_pattern(
            full_text,
            r"(?:invoice\s*number|#|no\.?)\s*[:\s]+(?:</?\w+>)*\s*([A-Za-z0-9\-]+)",
            "number",
        )
    if not invoice_number or not _looks_like_invoice_number(invoice_number):
        invoice_number = _find_pattern(
            full_text,
            r"invoice\s*#?\s*:?\s*(?:</?\w+>)*\s*([A-Z]{2,4}[-\s]?\d[\w\-]*)",
            "invoice_alt",
        )
    if not invoice_number or not _looks_like_invoice_number(invoice_number):
        invoice_number = _find_invoice_number_anywhere(full_text)
    invoice_number = (invoice_number or "UNKNOWN").strip()
    vendor_from_file = _vendor_from_filename(pdf_path)
    vendor_from_text = _find_pattern(full_text, r"(?:from|vendor|seller)\s*[:\s]*([A-Za-z0-9\s&\.,\-]+?)(?:\n|$|invoice)", "vendor")
    vendor_name = vendor_from_file if _looks_like_course_invoice(pdf_path) else (vendor_from_text or vendor_from_file)
    invoice_date = _find_date(full_text, "invoice", "date") or "2024-01-01"
    due_date = _find_date(full_text, "due", "due") or invoice_date

    line_items = _parse_line_items_from_tables(all_tables, full_text)
    if not line_items:
        amounts = re.findall(r"\$\s*([\d,]+(?:\.\d{2})?)", full_text)
        totals = [float(a.replace(",", "")) for a in amounts]
        total_amount = totals[-1] if totals else 0.0
        line_items = [{"description": "Invoice total", "quantity": 1, "unit_price": total_amount, "total": total_amount}]

    calculated_subtotal = sum(item["total"] for item in line_items)
    amounts = re.findall(r"\$\s*([\d,]+(?:\.\d{2})?)", full_text)
    total_amount = float(amounts[-1].replace(",", "")) if amounts else calculated_subtotal
    tax = round(total_amount - calculated_subtotal, 2)
    subtotal = calculated_subtotal

    return {
        "invoice_number": invoice_number.strip(),
        "vendor_name": vendor_name.strip(),
        "invoice_date": invoice_date,
        "due_date": due_date,
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "total_amount": round(total_amount, 2),
        "line_items": line_items,
        "notes": "",
    }


def _looks_like_invoice_number(s: str) -> bool:
    if not s or len(s) < 4:
        return False
    s_lower = s.lower()
    if s_lower in ("invoice", "oice", "number", "no", "inv"):
        return False
    if not re.match(r"^[A-Z]{2,}", s):
        return False
    if re.search(r"\d", s):
        return True
    if re.match(r"^[A-Z]{2,4}[-\s]?\d", s, re.IGNORECASE):
        return True
    return False


def _find_invoice_number_anywhere(text: str) -> str | None:
    header = text[:1500]
    m = re.search(r"\b([A-Z]{2,4}-\d[\w\-]*)\b", header, re.IGNORECASE)
    if m and _looks_like_invoice_number(m.group(1)):
        return m.group(1)
    m = re.search(r"\b([A-Z]{2,4}[-\s]?\d[\w\-]*)\b", header, re.IGNORECASE)
    if m and _looks_like_invoice_number(m.group(1)):
        return m.group(1)
    return None


def _find_pattern(text: str, pattern: str, _label: str) -> str | None:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _find_date(text: str, *keywords) -> str | None:
    for kw in keywords:
        m = re.search(rf"{kw}.{{0,30}}?(\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})", text, re.IGNORECASE)
        if m:
            return m.group(1)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else None


def _looks_like_course_invoice(pdf_path: str) -> bool:
    import os
    name = os.path.basename(pdf_path).lower()
    return name.startswith("invoice-") and name.endswith(".pdf")


def _vendor_from_filename(pdf_path: str) -> str:
    import os
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    parts = name.replace("invoice-", "").replace("-", " ").split()
    if parts:
        if parts[0].isdigit():
            parts = parts[1:]
        return " ".join(p.capitalize() for p in parts) if parts else "Unknown"
    return "Unknown"


def _parse_line_items_from_tables(tables: list, full_text: str) -> list:
    line_items = []
    for table in tables:
        if not table or len(table) < 2:
            continue
        header = [str(c).lower() if c else "" for c in table[0]]
        desc_col = _col_index(header, ["description", "item", "product", "service"])
        qty_col = _col_index(header, ["qty", "quantity", "qty."])
        unit_col = _col_index(header, ["unit price", "price", "rate", "unit"])
        total_col = _col_index(header, ["total", "amount", "extended", "line total"])
        if desc_col is None and total_col is None:
            continue
        for row in table[1:]:
            if not row:
                continue
            desc = str(row[desc_col]).strip() if desc_col is not None and desc_col < len(row) else (row[0] if row else "")
            if not desc or desc.lower() in ("subtotal", "tax", "total", "amount due"):
                continue
            qty = _parse_num(row[qty_col] if qty_col is not None and qty_col < len(row) else "1")
            unit = _parse_num(row[unit_col] if unit_col is not None and unit_col < len(row) else "0")
            total_val = _parse_num(row[total_col] if total_col is not None and total_col < len(row) else "0")
            if total_val == 0 and unit and qty:
                total_val = round(qty * unit, 2)
            if unit == 0 and total_val and qty:
                unit = round(total_val / qty, 2)
            if desc:
                line_items.append({"description": desc, "quantity": qty, "unit_price": unit, "total": total_val})
    return line_items


def _col_index(header: list, names: list) -> int | None:
    for i, h in enumerate(header):
        if any(n in h for n in names):
            return i
    return None


def _parse_num(s) -> float:
    if s is None:
        return 0.0
    s = str(s).replace(",", "").replace("$", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


# Lazy import so we don't require pdfplumber at module load (allows tests)
import pdfplumber  # noqa: E402
