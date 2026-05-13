from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TestCaseResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_case_id: int
    suite_run_id: int | None
    status: str
    failure_reason: str | None
    actual_status_code: int | None
    actual_response_time_ms: float | None
    response_preview: dict[str, Any] | list[Any] | str | None
    created_at: datetime


class TestSuiteRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suite_id: int
    status: str
    total_tests: int
    passed_count: int
    failed_count: int
    total_duration_ms: float
    summary: str | None
    created_at: datetime
    results: list[TestCaseResultResponse] = []
