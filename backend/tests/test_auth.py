"""Integration tests for the /auth router using an in-memory SQLite database."""


def test_register_success(client):
    response = client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "Password1",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    payload = {"full_name": "User", "email": "dupe@example.com", "password": "Password1"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "full_name": "Login User",
        "email": "login@example.com",
        "password": "Password1",
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "Password1",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "Wrong", "email": "wrong@example.com", "password": "Password1",
    })
    response = client.post("/auth/login", json={
        "email": "wrong@example.com", "password": "BadPassword9",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com", "password": "Password1",
    })
    assert response.status_code == 401


def test_logout_success(client):
    reg = client.post("/auth/register", json={
        "full_name": "Logout User", "email": "logout@example.com", "password": "Password1",
    })
    refresh_token = reg.json()["refresh_token"]
    response = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert response.status_code == 200


def test_refresh_token_rotation(client):
    """After refresh, old token must be rejected and new token must work."""
    reg = client.post("/auth/register", json={
        "full_name": "Rotate", "email": "rotate@example.com", "password": "Password1",
    })
    old_refresh = reg.json()["refresh_token"]

    # First refresh — should succeed and return a NEW refresh token
    r1 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r1.status_code == 200
    new_tokens = r1.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != old_refresh

    # Old refresh token must now be rejected (revoked)
    r2 = client.post("/auth/refresh", json={"refresh_token": old_refresh})
    assert r2.status_code == 401

    # New refresh token must still work
    r3 = client.post("/auth/refresh", json={"refresh_token": new_tokens["refresh_token"]})
    assert r3.status_code == 200


def test_forgot_password_always_200(client):
    """Anti-enumeration: same response whether email exists or not."""
    r1 = client.post("/auth/forgot-password", json={"email": "exists@example.com"})
    r2 = client.post("/auth/forgot-password", json={"email": "ghost@example.com"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["message"] == r2.json()["message"]
