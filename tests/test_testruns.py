from unittest.mock import patch

from tests.test_api_test_cases import _create_project, _headers


def _create_case(client, headers, project_id, **overrides):
    payload = {
        "name": "Health endpoint",
        "http_method": "GET",
        "url": "https://api.example.com/health",
        "expected_status_code": 200,
        "expected_response_time_ms": 500,
        "expected_json_field": "status",
        "expected_json_value": "ok",
    }
    payload.update(overrides)
    response = client.post(f"/projects/{project_id}/test-cases", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def test_run_test_case_passed(client):
    headers = _headers(client, "run-pass@example.com")
    project_id = _create_project(client, headers)
    case_id = _create_case(client, headers, project_id)

    with patch("app.routers.testruns.execute_test_case", return_value={"status": "passed", "failure_reason": None, "actual_status_code": 200, "actual_response_time_ms": 10.0, "response_preview": {"status": "ok"}}):
        response = client.post(f"/test-cases/{case_id}/run", headers=headers)

    assert response.status_code == 201
    assert response.json()["status"] == "passed"


def test_run_test_case_failed_json_assertion(client):
    headers = _headers(client, "run-fail@example.com")
    project_id = _create_project(client, headers)
    case_id = _create_case(client, headers, project_id)

    with patch("app.routers.testruns.execute_test_case", return_value={"status": "failed", "failure_reason": "Expected JSON field 'status' to equal 'ok', got 'bad'", "actual_status_code": 200, "actual_response_time_ms": 11.0, "response_preview": {"status": "bad"}}):
        response = client.post(f"/test-cases/{case_id}/run", headers=headers)

    assert response.status_code == 201
    assert "Expected JSON field" in response.json()["failure_reason"]


def test_suite_execution_summary(client):
    headers = _headers(client, "suite-run@example.com")
    project_id = _create_project(client, headers)
    case_a = _create_case(client, headers, project_id, name="Case A")
    case_b = _create_case(client, headers, project_id, name="Case B")
    suite_id = client.post(f"/projects/{project_id}/test-suites", headers=headers, json={"name": "Suite", "description": "desc"}).json()["id"]
    client.post(f"/test-suites/{suite_id}/test-cases/{case_a}", headers=headers)
    client.post(f"/test-suites/{suite_id}/test-cases/{case_b}", headers=headers)

    side_effects = [
        {"status": "passed", "failure_reason": None, "actual_status_code": 200, "actual_response_time_ms": 10.0, "response_preview": {"status": "ok"}},
        {"status": "failed", "failure_reason": "Expected status 200, got 500", "actual_status_code": 500, "actual_response_time_ms": 12.0, "response_preview": {"status": "error"}},
    ]
    with patch("app.routers.testruns.execute_test_case", side_effect=side_effects):
        run = client.post(f"/test-suites/{suite_id}/run", headers=headers)

    assert run.status_code == 201
    body = run.json()
    assert body["total_tests"] == 2
    assert body["passed_count"] == 1
    assert body["failed_count"] == 1


def test_run_access_control(client):
    owner = _headers(client, "owner-runs@example.com")
    other = _headers(client, "other-runs@example.com")
    project_id = _create_project(client, owner)
    case_id = _create_case(client, owner, project_id)
    assert client.post(f"/test-cases/{case_id}/run", headers=other).status_code == 404
