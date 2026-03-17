def get_auth_headers(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_test_run(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/test-runs",
        json={
            "test_name": "Sample Test",
            "test_type": "api",
            "status": "passed",
            "result": "Everything OK",
            "execution_time": 1.5
        },
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["test_name"] == "Sample Test"
    assert data["test_type"] == "api"
    assert data["status"] == "passed"


def test_test_run_summary(client):
    headers = get_auth_headers(client)

    client.post(
        "/test-runs",
        json={
            "test_name": "Test 1",
            "test_type": "api",
            "status": "passed",
            "result": "OK",
            "execution_time": 1.0
        },
        headers=headers
    )

    client.post(
        "/test-runs",
        json={
            "test_name": "Test 2",
            "test_type": "api",
            "status": "failed",
            "result": "Error",
            "execution_time": 1.2
        },
        headers=headers
    )

    response = client.get("/test-runs/stats", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 2
    assert data["passed"] >= 1
    assert data["failed"] >= 1


def test_filter_test_runs_by_status(client):
    headers = get_auth_headers(client)

    client.post(
        "/test-runs",
        json={
            "test_name": "Passed Test",
            "test_type": "api",
            "status": "passed",
            "result": "OK",
            "execution_time": 1.0
        },
        headers=headers
    )

    client.post(
        "/test-runs",
        json={
            "test_name": "Failed Test",
            "test_type": "api",
            "status": "failed",
            "result": "Error",
            "execution_time": 1.2
        },
        headers=headers
    )

    response = client.get("/test-runs?status=passed", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(test_run["status"] == "passed" for test_run in data)


def test_sort_test_runs(client):
    headers = get_auth_headers(client)

    client.post(
        "/test-runs",
        json={
            "test_name": "Test A",
            "test_type": "api",
            "status": "passed",
            "result": "OK",
            "execution_time": 2.0
        },
        headers=headers
    )

    client.post(
        "/test-runs",
        json={
            "test_name": "Test B",
            "test_type": "api",
            "status": "passed",
            "result": "OK",
            "execution_time": 1.0
        },
        headers=headers
    )

    response = client.get("/test-runs?sort=execution_time", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 2
    assert data[0]["execution_time"] <= data[1]["execution_time"]


def test_create_test_run_invalid_type(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/test-runs",
        json={
            "test_name": "Bad Type Test",
            "test_type": "mobile",
            "status": "passed",
            "result": "Should fail",
            "execution_time": 1.0
        },
        headers=headers
    )

    assert response.status_code == 422