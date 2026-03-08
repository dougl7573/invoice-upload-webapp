# Invoice Upload Web App (Lesson 2.4)

A simple web app where users can upload a PDF invoice, see extracted data, edit if needed, and save to Airtable.

## What it does

1. **Upload** – User selects a PDF invoice.
2. **Process** – Backend extracts invoice number, vendor, date, amount, line items (using the same pipeline as Lesson 2.2).
3. **Review** – Extracted data is shown in editable fields.
4. **Save** – User clicks "Save to Airtable"; record is created in your Invoices base.

## Run locally

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file (copy from `.env.example`) in the project root or in `backend/`:

```
AIRTABLE_TOKEN=your_token_here
AIRTABLE_BASE_ID=your_base_id_here
```

Start the server:

```bash
python3 app.py
```

The app will be at **http://localhost:5000**. The backend serves the frontend and the API. (If port 5000 is in use, run `PORT=5002 python3 app.py` and open http://localhost:5002.)

### 2. Use the app

1. Open http://localhost:5000 in your browser.
2. Click "Choose PDF" and select an invoice PDF.
3. Click "Process Invoice".
4. Review (and edit) the extracted data.
5. Click "Save to Airtable".

## Project layout

- `backend/` – Flask app: `/api/process` (PDF → JSON), `/api/save` (JSON → Airtable). Includes its own extraction and transform (self-contained for Vercel).
- `frontend/` – Static HTML/CSS/JS (upload form, results, save button).
- `pyproject.toml` – Tells Vercel where the Flask app is (`backend.app:app`).
- `requirements.txt` (root) – Dependencies for Vercel build.
- `.env` – Your Airtable credentials (not committed; use `.env.example` as a template).

## Deploy to Vercel

1. **Push to GitHub**: Create a repo with the contents of `invoice-upload-webapp`, or use your course repo and set **Root Directory** in Vercel to `precision-manufacturing/invoice-upload-webapp`.
2. **Connect at [vercel.com](https://vercel.com)**: Add New → Project → import the repo. Set Root Directory if the app is in a subfolder.
3. **Environment variables**: In the project, go to Settings → Environment Variables and add `AIRTABLE_TOKEN` and `AIRTABLE_BASE_ID` (same values as your `.env`).
4. **Deploy**: Click Deploy. Vercel detects Flask via `pyproject.toml` and uses root `requirements.txt`. You get a URL like `your-project-xxx.vercel.app`.
5. **Test**: Open the URL, upload a PDF, process, and save to Airtable.

## Requirements

- Python 3.9+
- Airtable base with an "Invoices" table (same as Lesson 2.2).
