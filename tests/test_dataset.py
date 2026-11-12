"""Dataset tests: manual upload, validation, empty state, process-on-click only."""


def test_dashboard_empty_state_before_upload(logged_in):
    r = logged_in.get("/dashboard")
    assert b"Upload your loan dataset to begin analysing loan applications." in r.data
    assert b"No dataset yet" in r.data


def test_prediction_blocked_before_training(logged_in):
    r = logged_in.get("/prediction/new")
    assert b"Please upload and process a loan dataset before making predictions." in r.data


def test_upload_valid_csv_shows_real_summary(logged_in, sample_csv):
    with open(sample_csv, "rb") as fh:
        r = logged_in.post("/dataset/upload",
                           data={"csv_file": (fh, "sample.csv")},
                           content_type="multipart/form-data", follow_redirects=True)
    assert r.status_code == 200
    assert b"Dataset uploaded" in r.data
    # 60 rows in the fixture; 40 approved (i%3 != 0), 20 rejected.
    assert b"60" in r.data
    # Models must NOT be trained by upload alone.
    r = logged_in.get("/performance")
    assert b"No trained models yet" in r.data


def test_upload_rejects_non_csv(logged_in, tmp_path):
    bad = tmp_path / "data.txt"
    bad.write_text("not a csv")
    with open(bad, "rb") as fh:
        r = logged_in.post("/dataset/upload",
                           data={"csv_file": (fh, "data.txt")},
                           content_type="multipart/form-data", follow_redirects=True)
    assert b"Only CSV files are supported" in r.data


def test_upload_rejects_missing_column(logged_in, tmp_path):
    import pandas as pd
    df = pd.DataFrame([{"loan_id": 1, "no_of_dependents": 0}])
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)
    with open(path, "rb") as fh:
        r = logged_in.post("/dataset/upload",
                           data={"csv_file": (fh, "bad.csv")},
                           content_type="multipart/form-data", follow_redirects=True)
    assert b"Missing required column" in r.data


def test_process_trains_models(logged_in, sample_csv):
    with open(sample_csv, "rb") as fh:
        logged_in.post("/dataset/upload", data={"csv_file": (fh, "sample.csv")},
                       content_type="multipart/form-data", follow_redirects=True)
    r = logged_in.post("/dataset/process/1", data={}, follow_redirects=True)
    assert b"Training complete" in r.data
    assert b"Best model" in r.data
    r = logged_in.get("/performance")
    assert b"Decision Tree" in r.data
    assert b"Random Forest" in r.data
