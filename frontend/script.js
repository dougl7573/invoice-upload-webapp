(function () {
  const fileInput = document.getElementById("fileInput");
  const fileName = document.getElementById("fileName");
  const processBtn = document.getElementById("processBtn");
  const loading = document.getElementById("loading");
  const errorEl = document.getElementById("error");
  const resultsSection = document.getElementById("resultsSection");
  const invoiceNumber = document.getElementById("invoiceNumber");
  const vendor = document.getElementById("vendor");
  const invoiceDate = document.getElementById("invoiceDate");
  const dueDate = document.getElementById("dueDate");
  const amount = document.getElementById("amount");
  const lineItems = document.getElementById("lineItems");
  const saveBtn = document.getElementById("saveBtn");
  const saveStatus = document.getElementById("saveStatus");

  let lastInvoiceData = null;

  fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];
    if (file) {
      fileName.textContent = file.name;
      processBtn.disabled = false;
    } else {
      fileName.textContent = "";
      processBtn.disabled = true;
    }
    hideError();
    resultsSection.classList.add("hidden");
  });

  processBtn.addEventListener("click", async function () {
    const file = fileInput.files[0];
    if (!file) return;
    hideError();
    loading.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    processBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/process", {
        method: "POST",
        body: formData,
      });
      const data = await res.json().catch(() => ({}));
      loading.classList.add("hidden");
      processBtn.disabled = false;

      if (!res.ok) {
        showError(data.error || "Processing failed");
        return;
      }

      lastInvoiceData = data;
      invoiceNumber.value = data.invoice_number || "";
      vendor.value = data.vendor_name || "";
      invoiceDate.value = data.invoice_date || "";
      dueDate.value = data.due_date || "";
      amount.value = data.total_amount != null ? "$" + Number(data.total_amount).toFixed(2) : "";

      if (data.line_items && data.line_items.length) {
        lineItems.textContent = data.line_items
          .map(function (item) {
            return item.description + ": " + item.quantity + " × $" + item.unit_price + " = $" + item.total;
          })
          .join("\n");
      } else {
        lineItems.textContent = "";
      }

      resultsSection.classList.remove("hidden");
    } catch (err) {
      loading.classList.add("hidden");
      processBtn.disabled = false;
      showError(err.message || "Network error");
    }
  });

  saveBtn.addEventListener("click", async function () {
    if (!lastInvoiceData) return;
    hideError();
    saveStatus.textContent = "Saving…";
    saveStatus.className = "save-status";

    const payload = {
      invoice_number: invoiceNumber.value.trim() || lastInvoiceData.invoice_number,
      vendor_name: vendor.value.trim() || lastInvoiceData.vendor_name,
      invoice_date: invoiceDate.value.trim() || lastInvoiceData.invoice_date,
      due_date: dueDate.value.trim() || lastInvoiceData.due_date,
      total_amount: lastInvoiceData.total_amount,
      subtotal: lastInvoiceData.subtotal,
      tax: lastInvoiceData.tax,
      line_items: lastInvoiceData.line_items || [],
      notes: lastInvoiceData.notes || "",
    };

    try {
      const res = await fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.success) {
        saveStatus.textContent = "Saved to Airtable. Record ID: " + (data.airtable_record_id || "");
        saveStatus.className = "save-status success";
      } else {
        saveStatus.textContent = data.error || "Save failed";
        saveStatus.className = "save-status fail";
      }
    } catch (err) {
      saveStatus.textContent = err.message || "Network error";
      saveStatus.className = "save-status fail";
    }
  });

  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.classList.remove("hidden");
  }

  function hideError() {
    errorEl.classList.add("hidden");
    errorEl.textContent = "";
  }
})();
