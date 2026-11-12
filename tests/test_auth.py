"""Auth tests: register, login, logout, protected routes, password change."""


def test_register_and_login(client):
    r = client.post("/register", data={
        "name": "Hakeem", "email": "hakeem@example.com",
        "password": "secret123", "confirm_password": "secret123",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"Dashboard" in r.data
    # Logout, then login again with the same credentials.
    client.get("/logout", follow_redirects=True)
    r = client.post("/login", data={"email": "hakeem@example.com", "password": "secret123"},
                    follow_redirects=True)
    assert b"Dashboard" in r.data


def test_login_wrong_password_rejected(client, logged_in):
    client.get("/logout", follow_redirects=True)
    r = client.post("/login", data={"email": "test@example.com", "password": "wrongpass"},
                    follow_redirects=True)
    assert b"Invalid email or password" in r.data


def test_protected_routes_redirect_when_logged_out(client):
    for url in ("/dashboard", "/dataset", "/performance", "/prediction/new",
                "/prediction/history", "/settings"):
        r = client.get(url, follow_redirects=False)
        assert r.status_code == 302, url
        assert "/login" in r.headers["Location"]


def test_password_change_works(logged_in):
    r = logged_in.post("/settings", data={
        "action": "password", "current_password": "secret123",
        "new_password": "newpass456", "confirm_password": "newpass456",
    }, follow_redirects=True)
    assert b"Password changed successfully" in r.data
    logged_in.get("/logout", follow_redirects=True)
    r = logged_in.post("/login", data={"email": "test@example.com", "password": "newpass456"},
                       follow_redirects=True)
    assert b"Dashboard" in r.data


def test_forgot_password_resets(logged_in):
    logged_in.get("/logout", follow_redirects=True)
    r = logged_in.post("/forgot", data={
        "email": "test@example.com", "password": "reset789",
        "confirm_password": "reset789",
    }, follow_redirects=True)
    assert b"Password reset" in r.data
    r = logged_in.post("/login", data={"email": "test@example.com", "password": "reset789"},
                       follow_redirects=True)
    assert b"Dashboard" in r.data
