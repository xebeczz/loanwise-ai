# Demo dataset (Render auto-seed only)

`demo_dataset.csv` is the Kaggle Loan Approval Prediction Dataset
(Archit Sharma, 4,269 rows, 13 columns, 2,656 Approved / 1,613
Rejected, 0 missing values) — the same file used for all the verified
results (Random Forest best, 98.36%).

It exists ONLY so the Render deployment can restore itself after the
free tier wipes the database on a restart (see `../seed.py`). It is
never used on a local run: locally the app still starts empty and the
user must upload a CSV manually through Dataset Management and click
"Process Dataset & Train Models" — that is the college flow.
