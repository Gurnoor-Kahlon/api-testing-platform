def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "testtoken123"
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_login_invalid_username(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "wronguser",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}