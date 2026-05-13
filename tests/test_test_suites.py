from tests.test_api_test_cases import _create_project, _headers


def _create_case(client, headers, project_id, name="Case"):
    payload = {
        "name": name,
        "http_method": "GET",
        "url": "https://api.example.com/test",
        "expected_status_code": 200,
        "expected_response_time_ms": 1000,
    }
    response = client.post(f"/projects/{project_id}/test-cases", headers=headers, json=payload)
    return response.json()["id"]


def test_test_suite_crud_and_case_relationships(client):
    headers = _headers(client, "suite@example.com")
    project_id = _create_project(client, headers)
    case_a = _create_case(client, headers, project_id, "Case A")
    case_b = _create_case(client, headers, project_id, "Case B")

    created = client.post(f"/projects/{project_id}/test-suites", headers=headers, json={"name": "Regression", "description": "Nightly checks"})
    assert created.status_code == 201
    suite_id = created.json()["id"]

    add_a = client.post(f"/test-suites/{suite_id}/test-cases/{case_a}", headers=headers)
    assert add_a.status_code == 200
    assert case_a in add_a.json()["test_case_ids"]

    add_b = client.post(f"/test-suites/{suite_id}/test-cases/{case_b}", headers=headers)
    assert case_b in add_b.json()["test_case_ids"]

    remove_a = client.delete(f"/test-suites/{suite_id}/test-cases/{case_a}", headers=headers)
    assert remove_a.status_code == 200
    assert case_a not in remove_a.json()["test_case_ids"]

    updated = client.put(f"/test-suites/{suite_id}", headers=headers, json={"name": "Smoke"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Smoke"

    deleted = client.delete(f"/test-suites/{suite_id}", headers=headers)
    assert deleted.status_code == 204


def test_test_suite_auth_and_cross_project_guard(client):
    headers_a = _headers(client, "a-suite@example.com")
    headers_b = _headers(client, "b-suite@example.com")

    project_a = _create_project(client, headers_a, "Project A")
    project_b = _create_project(client, headers_b, "Project B")
    case_a = _create_case(client, headers_a, project_a, "Case A")
    suite_a = client.post(f"/projects/{project_a}/test-suites", headers=headers_a, json={"name": "Suite A", "description": "x"}).json()["id"]

    assert client.get(f"/test-suites/{suite_a}", headers=headers_b).status_code == 404

    case_b = _create_case(client, headers_b, project_b, "Case B")
    mismatch = client.post(f"/test-suites/{suite_a}/test-cases/{case_b}", headers=headers_a)
    assert mismatch.status_code == 404

    assert client.post(f"/test-suites/{suite_a}/test-cases/{case_a}").status_code == 401
