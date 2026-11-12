"""Prediction + history + PDF tests (through the live test client)."""


def _train(logged_in, sample_csv):
    with open(sample_csv, "rb") as fh:
        logged_in.post("/dataset/upload", data={"csv_file": (fh, "sample.csv")},
                       content_type="multipart/form-data", follow_redirects=True)
    logged_in.post("/dataset/process/1", data={}, follow_redirects=True)


SAMPLE_FORM = {
    "no_of_dependents": "0", "education": "Graduate", "self_employed": "Salaried",
    "income_annum": "4000000", "loan_amount": "11500000", "loan_term": "8",
    "cibil_score": "434", "residential_assets_value": "4500000",
    "commercial_assets_value": "2800000", "luxury_assets_value": "8400000",
    "bank_asset_value": "5900000",
}


def test_prediction_saved_and_history_lists_it(logged_in, sample_csv):
    _train(logged_in, sample_csv)
    r = logged_in.post("/prediction/new", data=SAMPLE_FORM, follow_redirects=True)
    assert r.status_code == 200
    assert (b"APPROVED" in r.data or b"REJECTED" in r.data
            or b"FURTHER REVIEW" in r.data)
    r = logged_in.get("/prediction/history")
    assert b"434" in r.data  # CIBIL score of the sample applicant


def test_prediction_validation_rejects_bad_cibil(logged_in, sample_csv):
    _train(logged_in, sample_csv)
    bad = dict(SAMPLE_FORM, cibil_score="950")
    r = logged_in.post("/prediction/new", data=bad, follow_redirects=True)
    assert b"CIBIL score must be between 300 and 900" in r.data


def test_prediction_pdf_download(logged_in, sample_csv):
    _train(logged_in, sample_csv)
    logged_in.post("/prediction/new", data=SAMPLE_FORM, follow_redirects=True)
    r = logged_in.get("/reports/prediction/1.pdf")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"
    assert r.data[:4] == b"%PDF"


def test_performance_pdf_download(logged_in, sample_csv):
    _train(logged_in, sample_csv)
    r = logged_in.get("/reports/performance.pdf")
    assert r.status_code == 200
    assert r.mimetype == "application/pdf"


def test_history_delete_with_confirmation(logged_in, sample_csv):
    _train(logged_in, sample_csv)
    logged_in.post("/prediction/new", data=SAMPLE_FORM, follow_redirects=True)
    r = logged_in.post("/prediction/history/1/delete", follow_redirects=True)
    assert b"deleted" in r.data
    r = logged_in.get("/prediction/history")
    assert b"No predictions yet" in r.data
