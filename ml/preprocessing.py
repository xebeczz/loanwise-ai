"""LoanWise AI - ML preprocessing.

Everything here works on the CSV the user uploaded manually.
Nothing is loaded from inside the project and nothing is hardcoded:
row counts, approved/rejected counts and missing values are all
calculated from the actual uploaded file.
"""
import pandas as pd

# The 13 columns the uploaded CSV must contain (spec section 5C).
REQUIRED_COLUMNS = [
    "loan_id",
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
    "loan_status",
]

# The 11 features fed to the models, in this exact order everywhere
# (training, prediction, feature importance). loan_id is dropped,
# loan_status is the target.
FEATURE_COLUMNS = [
    "no_of_dependents",
    "education",
    "self_employed",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]

TARGET_COLUMN = "loan_status"

# Human-readable names for the feature-importance chart / viva explanation.
FEATURE_LABELS = {
    "no_of_dependents": "Number of Dependents",
    "education": "Education",
    "self_employed": "Employment Status",
    "income_annum": "Annual Income",
    "loan_amount": "Loan Amount",
    "loan_term": "Loan Term",
    "cibil_score": "CIBIL Score",
    "residential_assets_value": "Residential Assets",
    "commercial_assets_value": "Commercial Assets",
    "luxury_assets_value": "Luxury Assets",
    "bank_asset_value": "Bank Assets",
}


def validate_csv(df):
    """Validate an uploaded dataframe. Returns a list of error strings (empty = OK)."""
    errors = []
    if df is None or df.empty:
        return ["The CSV file is empty - it has no rows."]
    # Duplicate column names.
    if len(df.columns) != len(set(df.columns)):
        errors.append("The CSV has duplicate column names.")
    # Required columns (case-insensitive match, then normalised below).
    lower = [str(c).strip().lower() for c in df.columns]
    for col in REQUIRED_COLUMNS:
        if col not in lower:
            errors.append(f"Missing required column: {col}")
    return errors


def clean_dataframe(df):
    """Strip whitespace from column names and string values."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None})
    return df


def summarise(df):
    """Summary cards for the Dataset page, calculated from the real CSV."""
    approved = int((df["loan_status"].astype(str).str.strip() == "Approved").sum())
    rejected = int((df["loan_status"].astype(str).str.strip() == "Rejected").sum())
    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "approved": approved,
        "rejected": rejected,
    }


def encode_features(df):
    """Encode the categorical columns exactly as the spec says.

    education:     Graduate = 1, Not Graduate = 0
    self_employed: Yes = 1, No = 0
    loan_status:   Approved = 1, Rejected = 0
    Raises ValueError on an unexpected categorical value.
    """
    df = df.copy()
    edu_map = {"Graduate": 1, "Not Graduate": 0}
    emp_map = {"Yes": 1, "No": 0}
    status_map = {"Approved": 1, "Rejected": 0}
    for col, mapping in (("education", edu_map),
                         ("self_employed", emp_map),
                         ("loan_status", status_map)):
        bad = sorted(set(df[col].astype(str).str.strip()) - set(mapping))
        if bad:
            raise ValueError(f"Unexpected value(s) in column '{col}': {', '.join(bad)}")
        df[col] = df[col].astype(str).str.strip().map(mapping)
    return df


def applicant_to_features(applicant):
    """Turn the 11 prediction-form values into one model input row.

    applicant: dict with keys no_of_dependents, education ('Graduate' /
    'Not Graduate'), self_employed ('Yes' / 'No' - form sends
    'Self-employed' / 'Salaried'), income_annum, loan_amount, loan_term,
    cibil_score, residential_assets_value, commercial_assets_value,
    luxury_assets_value, bank_asset_value.
    Returns a one-row DataFrame with FEATURE_COLUMNS in order.
    """
    emp = applicant["self_employed"]
    emp_value = 1 if str(emp).strip().lower().startswith("self") or str(emp).strip() == "Yes" else 0
    row = {
        "no_of_dependents": int(applicant["no_of_dependents"]),
        "education": 1 if str(applicant["education"]).strip() == "Graduate" else 0,
        "self_employed": emp_value,
        "income_annum": float(applicant["income_annum"]),
        "loan_amount": float(applicant["loan_amount"]),
        "loan_term": int(applicant["loan_term"]),
        "cibil_score": int(applicant["cibil_score"]),
        "residential_assets_value": float(applicant["residential_assets_value"]),
        "commercial_assets_value": float(applicant["commercial_assets_value"]),
        "luxury_assets_value": float(applicant["luxury_assets_value"]),
        "bank_asset_value": float(applicant["bank_asset_value"]),
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)
