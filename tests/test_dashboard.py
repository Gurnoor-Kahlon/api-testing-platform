from datetime import datetime, timedelta

from app.models import APITestCase, Project, TestCaseResult, TestSuite
from tests.conftest import TestingSessionLocal


def _seed_data(owner_id: int):
    db = TestingSessionLocal()
    try:
        project = Project(name="Core API", description="", owner_id=owner_id)
        db.add(project)
        db.flush()

        case_one = APITestCase(project_id=project.id, name="Users API", http_method="GET", url="https://example.com/users", expected_status_code=200, expected_response_time_ms=500)
        case_two = APITestCase(project_id=project.id, name="Orders API", http_method="POST", url="https://example.com/orders", expected_status_code=201, expected_response_time_ms=500)
        suite = TestSuite(project_id=project.id, name="Smoke", description="")
        db.add_all([case_one, case_two, suite])
        db.flush()

        now = datetime.utcnow()
        db.add_all([
            TestCaseResult(test_case_id=case_one.id, status="passed", actual_status_code=200, actual_response_time_ms=120, created_at=now - timedelta(days=1)),
            TestCaseResult(test_case_id=case_two.id, status="failed", failure_reason="500 received", actual_status_code=500, actual_response_time_ms=340, created_at=now),
        ])
        db.commit()
    finally:
        db.close()


def test_dashboard_summary(client, auth_headers):
    _seed_data(1)
    response = client.get('/dashboard/summary', headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body['total_projects'] == 1
    assert body['total_test_cases'] == 2
    assert body['total_test_suites'] == 1
    assert body['total_test_runs'] == 2
    assert body['total_passed_runs'] == 1
    assert body['total_failed_runs'] == 1
    assert body['overall_pass_rate'] == 50.0
    assert body['average_response_time_ms'] == 230.0
    assert len(body['latest_test_runs']) == 2
    assert len(body['latest_failed_tests']) == 1


def test_dashboard_aux_endpoints(client, auth_headers):
    _seed_data(1)
    recent_runs = client.get('/dashboard/recent-runs', headers=auth_headers)
    failures = client.get('/dashboard/failures', headers=auth_headers)
    pass_rate = client.get('/dashboard/pass-rate', headers=auth_headers)

    assert recent_runs.status_code == 200
    assert failures.status_code == 200
    assert pass_rate.status_code == 200
    assert pass_rate.json()['pass_rate'] == 50.0
    assert failures.json()[0]['failure_reason'] == '500 received'
