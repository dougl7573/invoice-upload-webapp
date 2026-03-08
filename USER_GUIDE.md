# Invoice Upload Tool – User Guide (Finance)

## What this does

The Invoice Upload Tool takes a PDF invoice, pulls out the key details (invoice number, vendor, date, amount, line items), and saves a record to Airtable. You can review and edit the data before saving.

---

## How to use it

### 1. Open the tool

- **If it’s running locally:** Open this link in your browser: **http://localhost:5002** (or the URL your team gave you).
- **If it’s deployed:** Use the link from your team (e.g. `https://your-invoice-app.vercel.app`).

### 2. Choose your invoice PDF

- Click **Choose PDF** (or the file button).
- Select the invoice PDF from your computer. Only PDF files are accepted.

### 3. Process the invoice

- Click **Process Invoice**.
- Wait a few seconds. You’ll see “Processing…” then the **Extracted Data** section will appear.

### 4. Review and edit (if needed)

- Check **Invoice Number**, **Vendor**, **Invoice Date**, **Due Date**, and **Amount**.
- If anything is wrong or missing, type in the boxes to correct it. The **Amount** field is filled from the PDF but can’t be edited (it’s used as-is for Airtable).
- Line items are shown below for reference.

### 5. Save to Airtable

- When everything looks correct, click **Save to Airtable**.
- Wait for the “Saved to Airtable” message. You’re done.
- You can confirm in your Airtable Invoices table that the new record is there.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **“Processing…” never finishes** | The PDF may be very large or corrupted. Try a different file or a smaller PDF. |
| **Extracted data is wrong or missing** | Edit the fields in the form before clicking Save. The tool does its best to read the PDF but may need manual fixes. |
| **“Save to Airtable” fails or shows an error** | The tool may be misconfigured or Airtable may be unavailable. Contact your IT or the person who set up the tool. |
| **Upload fails or “File must be a PDF”** | Make sure the file is a PDF (not a scanned image saved as Word, etc.). Use “Save as PDF” or export to PDF if needed. |
| **Page won’t load** | Check your internet connection. If using a local link (localhost), make sure the person who runs the tool has started it. |

---

## What works best

- **Standard PDF invoices** with clear text (invoice number, vendor name, dates, dollar amounts).
- **One invoice per PDF** (one upload = one Airtable record).
- **Reasonable file size** (typical invoices are fine; very large scans may be slow or fail).

The tool may need manual review for:

- Handwritten or unclear text  
- Invoices in other languages  
- Poor-quality scans  
- Unusual layouts  

When in doubt, check the extracted data and fix it before saving.

---

## Who to contact

For access, errors, or questions about the tool, contact the person who set up the Invoice Upload Tool or your IT/Finance lead.
