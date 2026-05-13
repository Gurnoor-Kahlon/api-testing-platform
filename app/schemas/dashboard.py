from datetime import datetime

from pydantic import BaseModel


class DashboardRecentRun(BaseModel):
    id: int
    test_case_id: int
    project_name: str
    status: str
    actual_response_time_ms: float | None
    created_at: datetime


class DashboardFailure(BaseModel):
    id: int
    test_case_id: int
    project_name: str
    failure_reason: str | None
    created_at: datetime


class DashboardTrendPoint(BaseModel):
    date: str
    passed: int
    failed: int


class DashboardSummaryResponse(BaseModel):
    total_projects: int
    total_test_cases: int
    total_test_suites: int
    total_test_runs: int
    total_passed_runs: int
    total_failed_runs: int
    overall_pass_rate: float
    average_response_time_ms: float | None
    most_recently_updated_project: str | None
    trend: list[DashboardTrendPoint]
    latest_test_runs: list[DashboardRecentRun]
    latest_failed_tests: list[DashboardFailure]
