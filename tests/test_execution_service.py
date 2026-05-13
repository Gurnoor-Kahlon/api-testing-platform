import httpx
from unittest.mock import Mock, patch

from app.models.api_test_case import APITestCase
from app.services.test_execution_service import execute_test_case


def _case(**kwargs):
    base = dict(
        id=1, project_id=1, name="case", http_method="GET", url="https://api.example.com", headers=None, query_params=None,
        request_body=None, expected_status_code=200, expected_response_time_ms=1000, expected_json_field="status", expected_json_value="ok"
    )
    base.update(kwargs)
    return APITestCase(**base)


def test_execute_passed():
    response = Mock(status_code=200)
    response.json.return_value = {"status": "ok"}
    with patch("httpx.Client.request", return_value=response):
        result = execute_test_case(_case())
    assert result["status"] == "passed"


def test_execute_failed_status_and_threshold():
    response = Mock(status_code=500)
    response.json.return_value = {"status": "ok"}
    with patch("httpx.Client.request", return_value=response), patch("time.perf_counter", side_effect=[0.0, 1.0]):
        result = execute_test_case(_case(expected_response_time_ms=10))
    assert result["status"] == "failed"
    assert "Expected status" in result["failure_reason"]
    assert "Expected response time" in result["failure_reason"]


def test_execute_connection_failure():
    with patch("httpx.Client.request", side_effect=httpx.ConnectError("no route")):
        result = execute_test_case(_case(headers={"Authorization": "secret"}))
    assert result["status"] == "failed"
    assert result["response_preview"]["request_headers"]["Authorization"] == "***"
