def test_register_success(client):
    response = client.post("/auth/register", json={"email": "dev@example.com", "full_name": "Dev User", "password": "SecurePass123"})
    assert response.status_code == 201
    assert "password" not in response.text


def test_login_success(client):
    client.post("/auth/register", json={"email": "admin@example.com", "full_name": "Admin", "password": "password123"})
    response = client.post("/auth/login", json={"email": "admin@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_success(client):
    client.post("/auth/register", json={"email": "me@example.com", "full_name": "Me", "password": "password123"})
    login = client.post("/auth/login", json={"email": "me@example.com", "password": "password123"})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
