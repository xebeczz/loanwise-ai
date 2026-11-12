# Deploy LoanWise AI on Render (free)

Same pattern as Smart Attendance. Do **not** deploy from this VM —
create the repo and the Render service in the browser.

## 1. Create the GitHub repo (browser)

The GitHub App cannot create repos, so do it yourself:

1. Go to https://github.com/new
2. Repository name: `loanwise-ai`
3. Owner: `xebeczz`, Public, **do not** add a README / .gitignore / licence
   (the project already has them).
4. Create repository.

## 2. Push this project

```powershell
cd loanwise-ai
git init
git add .
git commit -m "LoanWise AI — Render-ready"
git branch -M main
git remote add origin https://github.com/xebeczz/loanwise-ai.git
git push -u origin main
```

What gets pushed: the Flask app, templates, tests and `stitch-reference/`
(the Stitch design source). What does **not** get pushed (see `.gitignore`):
`.venv/`, `__pycache__/`, `*.db`, uploaded CSVs, trained `.joblib` models,
charts and PDFs. The live site starts empty — no dataset, no models.

## 3. Create the Render service (browser)

1. Go to https://dashboard.render.com → **New +** → **Web Service**.
2. Pick the `xebeczz/loanwise-ai` repo.
3. Render reads `render.yaml` automatically: Python, free plan,
   build `pip install -r requirements.txt`,
   start `gunicorn app:app --bind 0.0.0.0:$PORT`.
   `SECRET_KEY` is generated for you; `FLASK_ENV=production`.
4. Click **Create Web Service**, then **Manual Deploy → Deploy latest commit**
   if it does not start by itself.
5. Wait for "Live" (first build takes a few minutes — scikit-learn /
   pandas are large). Free tier spins down after ~15 minutes idle, so
   the first load after a pause is slow (~30 s) — that is normal.

## 4. First use on the live site

The live site starts empty, exactly like a fresh local run:

1. Open the Render URL and click **Create an account** — register fresh.
2. Open **Dataset Management** → Browse CSV → select
   `loan_approval_dataset.csv` (4,269 rows) → **Upload**.
3. Inspect the summary cards and preview.
4. Click **Process Dataset & Train Models** and wait for training.
5. Open **Model Performance**, then **New Prediction**.

## ⚠️ Important — Render free disk is ephemeral

Render's free plan has **no persistent disk**. The SQLite database
(`loanwise.db`), uploaded CSVs, trained models and charts live on the
service's temporary disk, so **every redeploy / restart wipes them** —
same as Smart Attendance. After any redeploy you must:

- Register a fresh account on the live site, then
- Re-upload the CSV and click **Process Dataset & Train Models** again.

Your code and the Stitch design are safe in GitHub; only the live
data resets. Do not treat the live site as permanent storage.
