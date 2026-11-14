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
(the Stitch design source), plus `data/demo_dataset.csv` and `seed.py`
(the Render-only auto-seed — see below). What does **not** get pushed
(see `.gitignore`): `.venv/`, `__pycache__/`, `*.db`, uploaded CSVs,
trained `.joblib` models, charts and PDFs.

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

Since the 2026-11-14 auto-seed fix, the live site restores itself:
on startup, if the database is empty, it loads the bundled demo
dataset and trains the 5 models, and creates the demo account. Just
log in — no upload or training needed on the live link:

- Email: `retrain@loanwise.ai`
- Password: `Retrain1234!`

You can still register your own account — the trained models are
shared — and you can still upload a different CSV and train it
manually from Dataset Management (tick the replacement box).

## ⚠️ Important — Render free disk is ephemeral (auto-seed covers it)

Render's free plan has **no persistent disk**. The SQLite database
(`loanwise.db`), uploaded CSVs, trained models and charts live on the
service's temporary disk, so **every redeploy / restart wipes them** —
same as Smart Attendance. That wiped this demo twice before the fix.

`seed.py` covers it: on Render only, at startup, with an empty
database, it re-creates the demo from `data/demo_dataset.csv`
(4,269 rows) using the exact same training code as the manual
"Process Dataset & Train Models" button, and re-creates the demo
account. First boot after a wipe takes ~20 s longer for training;
after that the live link works again by itself. It never runs locally
(local runs stay empty + manual-upload-only) and never touches a
database that already has a dataset in it. Set
`LOANWISE_AUTO_SEED=0` to switch it off.

Your code and the Stitch design are safe in GitHub; only the live
data resets, and now it restores itself. Do not treat the live site
as permanent storage — your own accounts and predictions can still
be wiped by a restart, even though the demo dataset comes back.
