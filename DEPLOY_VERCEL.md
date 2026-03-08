# Deploy Invoice Upload Web App to Vercel (no GitHub)

Use these steps to deploy straight to Vercel without using GitHub.

---

## 1. Install the Vercel CLI (one time)

```bash
npm install -g vercel
```

If you don't use npm:

```bash
brew install vercel-cli
```

---

## 2. Log in

```bash
vercel login
```

Complete the login (email or GitHub).

---

## 3. Deploy from the web app folder

```bash
cd /Users/DougLoud/DocumentsMacBook/TCClaudeCodeCourse/Claude-Code-AI-Operator-Course/precision-manufacturing/invoice-upload-webapp
vercel
```

- **First run:** It will ask to link or create a project; you can accept the defaults (or choose a project name).
- It uploads the folder and deploys, then gives you a URL.

---

## 4. Add Airtable env vars

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard) → your project.
2. **Settings** → **Environment Variables**.
3. Add:
   - **Name:** `AIRTABLE_TOKEN`  
     **Value:** (your Airtable token, same as in `.env`)
   - **Name:** `AIRTABLE_BASE_ID`  
     **Value:** (your base ID, e.g. `app...`)
4. Save.

---

## 5. Redeploy so the new vars are used

- **Deployments** → open the **⋮** on the latest deployment → **Redeploy**.

---

## 6. Test

- Open the URL Vercel gave you.
- Upload a PDF, process it, then Save to Airtable.

---

## Later: deploy again from the same folder

```bash
cd /Users/DougLoud/DocumentsMacBook/TCClaudeCodeCourse/Claude-Code-AI-Operator-Course/precision-manufacturing/invoice-upload-webapp
vercel
```

Use `vercel --prod` when you want to update the production URL.
