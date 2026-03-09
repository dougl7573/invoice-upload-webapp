# Deploy Invoice Upload Web App: GitHub → Vercel (Lesson 2.4)

Use these steps to connect your GitHub repo to Vercel and get a live URL. Every push to `main` will trigger a new deployment.

---

## 1. Sign in to Vercel (with GitHub)

1. Go to **[vercel.com](https://vercel.com)** and click **Sign Up** or **Log In**.
2. Choose **Continue with GitHub**.
3. Authorize Vercel to access your GitHub account (you can limit it to specific repos if you prefer).

---

## 2. Import the project from GitHub

1. In the Vercel dashboard, click **Add New…** → **Project** (or go to **[vercel.com/new](https://vercel.com/new)**).
2. Under **Import Git Repository**, find **invoice-upload-webapp** (from `dougl7573/invoice-upload-webapp`).
   - If you don’t see it, click **Adjust GitHub App Permissions** and grant Vercel access to the repo.
3. Click **Import** next to **invoice-upload-webapp**.

---

## 3. Configure the project (one-time)

On the import screen, Vercel should detect the project. Check:

| Setting | Value / note |
|--------|----------------|
| **Framework Preset** | Leave as **Other** or **Flask** if shown. |
| **Root Directory** | Leave **blank** (use repo root). |
| **Build Command** | Leave **blank** (no build step). |
| **Output Directory** | Leave **blank**. |
| **Install Command** | Leave default (`pip install -r requirements.txt` or similar). |

The repo uses `pyproject.toml` with `app = "backend.app:app"`, so Vercel will use the Flask app in `backend/app.py`.

Click **Deploy** (you can add env vars in the next step if you prefer).

---

## 4. Add Airtable environment variables

Deployments need your Airtable credentials. Add them in Vercel:

1. Open your project on Vercel → **Settings** → **Environment Variables**.
2. Add:

   | Name | Value | Environment |
   |------|--------|--------------|
   | `AIRTABLE_TOKEN` | Your Airtable API token (same as in `.env`) | Production, Preview |
   | `AIRTABLE_BASE_ID` | Your Airtable base ID (e.g. `app...`) | Production, Preview |

3. Click **Save** for each.

---

## 5. Redeploy so the new vars are used

1. Go to **Deployments**.
2. Open the **⋮** menu on the latest deployment.
3. Click **Redeploy** (no need to clear cache unless you changed build settings).

---

## 6. Get your URL and test

- Your app URL is shown on the deployment (e.g. `invoice-upload-webapp-xxx.vercel.app`) and on the project **Settings** → **Domains**.
- Open the URL in a browser.
- Upload a PDF → process → **Save to Airtable** and confirm it works.

---

## 7. Automatic deploys on push

- **Production:** Pushes to `main` deploy to your production URL.
- **Preview:** Other branches (or pull requests) get unique preview URLs.

No need to run `vercel` from your machine unless you want to test with `vercel dev` locally.

---

## Troubleshooting

- **Build fails:** Check the build log on Vercel. Ensure `requirements.txt` and `pyproject.toml` are in the repo root and that `backend/app.py` exists and defines `app`.
- **502 / “Application error”:** Confirm `AIRTABLE_TOKEN` and `AIRTABLE_BASE_ID` are set for the right environment (Production/Preview) and redeploy.
- **CORS or API errors in browser:** The Flask app enables CORS; if you add a custom domain later, ensure the frontend uses that domain for API calls.
