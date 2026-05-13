def _headers(client, email: str):
    client.post("/auth/register", json={"email": email, "full_name": "User", "password": "Password123"})
    token = client.post("/auth/login", json={"email": email, "password": "Password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_project(client, headers, name="Project"):
    response = client.post("/projects", headers=headers, json={"name": name, "description": "desc"})
    return response.json()["id"]


def test_test_case_crud_and_validation(client):
    headers = _headers(client, "cases@example.com")
    project_id = _create_project(client, headers)

    payload = {
        "name": "Health endpoint",
        "description": "checks health",
        "http_method": "GET",
        "url": "https://api.example.com/health",
        "headers": {"Accept": "application/json"},
        "query_params": {"region": "us"},
        "request_body": None,
        "expected_status_code": 200,
        "expected_response_time_ms": 500,
        "expected_json_field": "status",
        "expected_json_value": "ok",
    }
    created = client.post(f"/projects/{project_id}/test-cases", headers=headers, json=payload)
    assert created.status_code == 201
    case_id = created.json()["id"]

    listed = client.get(f"/projects/{project_id}/test-cases", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    details = client.get(f"/test-cases/{case_id}", headers=headers)
    assert details.status_code == 200

    updated = client.put(f"/test-cases/{case_id}", headers=headers, json={"expected_status_code": 204})
    assert updated.status_code == 200
    assert updated.json()["expected_status_code"] == 204

    deleted = client.delete(f"/test-cases/{case_id}", headers=headers)
    assert deleted.status_code == 204

    invalid_method = client.post(f"/projects/{project_id}/test-cases", headers=headers, json={**payload, "http_method": "FETCH"})
    assert invalid_method.status_code == 422

    invalid_url = client.post(f"/projects/{project_id}/test-cases", headers=headers, json={**payload, "url": "bad-url"})
    assert invalid_url.status_code == 422


def test_test_cases_are_isolated_by_owner(client):
    owner_headers = _headers(client, "owner-cases@example.com")
    other_headers = _headers(client, "other-cases@example.com")
    owner_project = _create_project(client, owner_headers, name="Owner Project")

    payload = {
        "name": "Owner Case",
        "http_method": "GET",
        "url": "https://api.example.com/owner",
        "expected_status_code": 200,
        "expected_response_time_ms": 1000,
    }
    created = client.post(f"/projects/{owner_project}/test-cases", headers=owner_headers, json=payload)
    case_id = created.json()["id"]

    assert client.get(f"/test-cases/{case_id}", headers=other_headers).status_code == 404
    assert client.get(f"/projects/{owner_project}/test-cases", headers=other_headers).status_code == 404
