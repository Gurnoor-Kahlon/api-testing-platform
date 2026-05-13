import time
from typing import Any

import httpx

from app.models.api_test_case import APITestCase

SENSITIVE_HEADERS = {"authorization", "cookie", "x-api-key"}


def _extract_json_field(data: Any, field_path: str) -> Any:
    current = data
    for key in field_path.split("."):
        if not isinstance(current, dict) or key not in current:
            raise KeyError(f"Field '{field_path}' not found in JSON response")
        current = current[key]
    return current


def _safe_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    return {k: ("***" if k.lower() in SENSITIVE_HEADERS else v) for k, v in headers.items()}


def execute_test_case(test_case: APITestCase) -> dict[str, Any]:
    start_time = time.perf_counter()
    failure_messages: list[str] = []
    actual_status_code: int | None = None
    response_preview: dict[str, Any] | list[Any] | str | None = None

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.request(
                method=test_case.http_method,
                url=test_case.url,
                headers=test_case.headers or {},
                params=test_case.query_params or {},
                json=test_case.request_body,
            )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        actual_status_code = response.status_code

        try:
            response_payload = response.json()
            response_preview = response_payload if isinstance(response_payload, (dict, list)) else str(response_payload)
        except ValueError:
            response_payload = None
            response_preview = response.text[:500]

        if response.status_code != test_case.expected_status_code:
            failure_messages.append(f"Expected status {test_case.expected_status_code}, got {response.status_code}")

        if test_case.expected_response_time_ms and elapsed_ms > test_case.expected_response_time_ms:
            failure_messages.append(
                f"Expected response time <= {test_case.expected_response_time_ms} ms, got {elapsed_ms:.2f} ms"
            )

        if test_case.expected_json_field:
            if not isinstance(response_payload, dict):
                failure_messages.append("Expected JSON object response for JSON field assertion")
            else:
                try:
                    actual_value = _extract_json_field(response_payload, test_case.expected_json_field)
                    if test_case.expected_json_value is not None and str(actual_value) != test_case.expected_json_value:
                        failure_messages.append(
                            f"Expected JSON field '{test_case.expected_json_field}' to equal '{test_case.expected_json_value}', got '{actual_value}'"
                        )
                except KeyError as error:
                    failure_messages.append(str(error))

        status = "passed" if not failure_messages else "failed"
        return {
            "status": status,
            "failure_reason": " | ".join(failure_messages) if failure_messages else None,
            "actual_status_code": actual_status_code,
            "actual_response_time_ms": elapsed_ms,
            "response_preview": response_preview,
        }
    except httpx.HTTPError as error:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "failed",
            "failure_reason": f"Request execution failed: {error}",
            "actual_status_code": actual_status_code,
            "actual_response_time_ms": elapsed_ms,
            "response_preview": {"request_headers": _safe_headers(test_case.headers)},
        }
