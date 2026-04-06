def test_register_success(client):
    response = client.post("/auth/register", json={
        "full_name": "Ahmad Test",
        "email": "ahmad@test.com",
        "password": "test1234"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "full_name": "User One",
        "email": "duplicate@test.com",
        "password": "test1234"
    })
    response = client.post("/auth/register", json={
        "full_name": "User Two",
        "email": "duplicate@test.com",
        "password": "test1234"
    })
    assert response.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={
        "full_name": "Login Test",
        "email": "login@test.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", json={
        "email": "login@test.com",
        "password": "test1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "full_name": "Wrong Pass",
        "email": "wrong@test.com",
        "password": "test1234"
    })
    response = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_wrong_email(client):
    response = client.post("/auth/login", json={
        "email": "notexist@test.com",
        "password": "test1234"
    })
    assert response.status_code == 401