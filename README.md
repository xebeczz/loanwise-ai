# LoanWise AI — Machine Learning-Based Loan Approval Decision Support System

A complete working Flask web application for a college mini project.
It analyses historical loan application data with **five machine learning
models** and predicts whether a new applicant's loan should be approved
or rejected, using a 5-model vote.

**UI:** the design comes from the Google Stitch export in
`stitch-reference/` (8 pages: Login, Dashboard, Dataset Management,
Model Performance, New Prediction, Prediction Result, Prediction
History, Settings). Colours: navy `#14243A`, royal blue `#315EAB`,
teal `#24B8A5`, background `#F4F7FB`. Headings Manrope, body Inter.

## How the app works — manual dataset upload (read this first)

There is **no dataset bundled inside this project**. The app starts
with no data at all, and no model is trained on startup.

The ONLY way models get trained is this flow:

1. Register an account (or sign in).
2. Open **Dataset Management**.
3. Click **Browse CSV File** (or drag-and-drop a CSV into the box).
4. Select your loan CSV — e.g. `loan_approval_dataset.csv`
   (Loan Approval Prediction Dataset, Archit Sharma — 4,269 rows).
5. Click **Upload**. The app validates the file (CSV only, max 20 MB,
   all 13 required columns, no empty file, no duplicate columns,
   no missing values) and shows the real summary cards
   (rows / columns / missing / duplicates / Approved / Rejected)
   plus a searchable, paginated preview of the actual rows.
6. Click **Process Dataset & Train Models**. ONLY now does training
   happen: encoding, 70/30 split (`random_state=42`, stratified),
   StandardScaler fitted on training data only, and all five models
   are trained and saved.

Before any upload, the Dashboard shows the empty state
*"Upload your loan dataset to begin analysing loan applications."*
with an Upload button — no fake statistics. The New Prediction page
blocks with *"Please upload and process a loan dataset before making
predictions."* until models are trained.

**Dataset replacement:** upload a new CSV later and click Process
again. Tick the confirmation box, and the new dataset becomes active
only after its training succeeds. Previous predictions are kept.

## The five models

Each model is a scikit-learn Pipeline: `StandardScaler` + classifier,
all trained on the same split.

| Model | Settings |
|---|---|
| Decision Tree | `DecisionTreeClassifier(random_state=42)` |
| Random Forest | `RandomForestClassifier(n_estimators=100, random_state=42)` |
| Naive Bayes | `GaussianNB()` |
| KNN | `KNeighborsClassifier(n_neighbors=5)` |
| Logistic Regression | `LogisticRegression(max_iter=1000, random_state=42)` |

**Voting rule:** 5 approval votes = APPROVED, 5 rejection votes =
REJECTED, mixed votes = FURTHER REVIEW.

**Sample applicant** (Try Sample Applicant button): 0 dependents,
Graduate, Salaried, income 4,000,000, loan 11,500,000, term 8 years,
CIBIL 434, residential 4,500,000, commercial 2,800,000,
luxury 8,400,000, bank 5,900,000.

## Run on Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

Upload your dataset yourself (10 steps):

1. Click **Create an account** and register.
2. Open **Dataset Management**.
3. Click **Browse CSV**.
4. Select `loan_approval_dataset.csv` from your computer.
5. Click **Upload**.
6. Inspect the summary cards and the dataset preview.
7. Click **Process Dataset & Train Models**.
8. Wait for training to complete.
9. Open **Model Performance** to see the real accuracies.
10. Open **New Prediction** and start making loan predictions.

## Live demo (Render)

Ready for a free Render deploy — see [DEPLOY_RENDER.md](DEPLOY_RENDER.md)
for the exact steps (create repo `xebeczz/loanwise-ai` in the browser,
push, then New Web Service in Render — `render.yaml` does the rest).

⚠️ **Render free disk is ephemeral — auto-seed fixes it:** every
redeploy / restart wipes the SQLite database, uploaded CSVs and
trained models, same as Smart Attendance. That wiped the live demo
twice (2026-11-13, 2026-11-14). Since the 2026-11-14 fix, the app
auto-restores itself on Render only (see `seed.py`): on startup, if
the database is empty, it loads the bundled demo dataset
(`data/demo_dataset.csv`, the same 4,269-row Kaggle file) and trains
the 5 models, and creates the demo account
`retrain@loanwise.ai` / `Retrain1234!`. First boot after a wipe takes
~20 s longer; after that the live link works again by itself. Local
runs are unaffected — they still start empty and manual-upload-only.
Set `LOANWISE_AUTO_SEED=0` to switch the auto-seed off.
The free service also spins down when idle, so the first load after
a pause is slow (~30 s).

## Run on Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Project structure

```
loanwise-ai/
├── app.py                 # App factory + entry point (python app.py)
├── config.py              # Settings (SQLite path, 20 MB upload limit)
├── requirements.txt       # Flask, pandas, scikit-learn, gunicorn (Render)
├── render.yaml            # Render free web service (gunicorn)
├── DEPLOY_RENDER.md       # Exact Render deploy steps
├── README.md
├── stitch-reference/      # Your Google Stitch UI export (design source of truth)
├── uploads/datasets/      # CSVs you upload through the website (starts empty)
├── models/saved_models/   # Trained model files (created only after you click Process)
├── static/charts/         # Matplotlib charts generated during training
├── reports/               # Generated PDF reports
├── ml/
│   ├── preprocessing.py   # Validation, summary, encoding, applicant rows
│   ├── training.py        # The five pipelines + 70/30 split + saving
│   ├── evaluation.py      # Accuracy/Precision/Recall/F1 + charts
│   └── prediction.py      # 5-model vote + APPROVED/REJECTED/FURTHER REVIEW
├── database/db.py         # SQLite models: users, datasets, predictions
├── routes/
│   ├── auth.py            # Login / register / forgot / logout
│   ├── dashboard.py       # Dashboard stats (real data only)
│   ├── dataset.py         # Upload, preview, process & train, performance
│   ├── prediction.py      # New prediction, result, history, delete
│   ├── reports.py         # PDF reports (ReportLab)
│   ├── settings.py        # Profile + change password
│   └── common.py          # login_required, active dataset, model loading
├── templates/             # Jinja2 pages in the Stitch design (8 pages)
├── static/css/ static/js/ # Small extras on top of the Stitch Tailwind design
└── tests/                 # pytest tests (auth, dataset, models, prediction, routes)
```

## Features

- Login / registration with hashed passwords, Flask sessions,
  protected routes, logout, forgot-password reset, remember me,
  show/hide password.
- Dashboard with real stats, approval donut, accuracy bars, loan
  status distribution, recent predictions table; honest empty state.
- Manual CSV upload (drag-drop / browse, 20 MB max) with validation,
  real summary cards, searchable paginated preview.
- Process & train on button click only; dataset replacement with
  confirmation; old predictions kept.
- Model Performance: 5 model cards, comparison table (Accuracy /
  Precision / Recall / F1), accuracy / precision / recall / F1 charts,
  best-model confusion matrix, Random Forest feature importance.
- New Prediction: exactly 11 inputs, sample applicant button, reset,
  full validation (CIBIL 300–900, positive income/loan/term,
  non-negative assets/dependents).
- Prediction Result: each model's vote, 5-vote decision banner
  (green / red / amber), applicant details, PDF download.
- Prediction History: SQLite storage, search, filter by decision,
  sort by date, view details, PDF download, delete with confirmation.
- Settings: profile, working change password, app info, logout.
- PDF reports: per-prediction and model-performance (ReportLab).

## Tests

```bash
.venv\Scripts\pytest -q        # Windows
pytest -q                      # Linux/Mac (venv active)
```

Tests cover auth, upload validation, the empty state, training only
on button click, the five models, the 70/30 split, the voting rule,
prediction + history + PDF downloads, and every page loading.

## Troubleshooting

- **"Please upload and process a loan dataset before making
  predictions."** — normal before training. Upload a CSV in Dataset
  Management, then click Process Dataset & Train Models.
- **Upload rejected** — check the file is a `.csv` under 20 MB with
  all 13 required columns and no missing values.
- **Training failed** — the error is shown on the Dataset page; the
  most common cause is an unexpected value in `education`
  (must be Graduate / Not Graduate), `self_employed` (Yes / No) or
  `loan_status` (Approved / Rejected).
- **Port 5000 busy** — stop the other Flask app, or run
  `python app.py` after changing the port in `app.py`.
- **Forgot password** — use the Forgot password link; this demo has
  no email server, so the reset happens directly on that page.

## Limitations

- Single-user demo design (one shared active dataset; accounts are
  separate logins but share the dataset/models).
- Tailwind CSS and Google Fonts load from CDNs, so the styled UI
  needs internet on first load; the Flask/ML logic itself is local.
- The forgot-password page resets directly without an email link
  (no mail server in a college demo).
- Charts are static PNGs generated at training time, not live charts.
