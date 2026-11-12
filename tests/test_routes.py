"""Route smoke tests: every page loads for a logged-in user, no 500s."""


def test_all_pages_load(logged_in):
    for url in ("/dashboard", "/dataset", "/performance", "/prediction/new",
                "/prediction/history", "/settings"):
        r = logged_in.get(url)
        assert r.status_code == 200, url


def test_login_page_loads_anonymous(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert b"LoanWise AI" in r.data
    r = client.get("/register")
    assert r.status_code == 200
    r = client.get("/forgot")
    assert r.status_code == 200
