from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models import APITestCase, Project, TestCaseResult, TestSuite, User
from app.schemas.dashboard import DashboardFailure, DashboardRecentRun, DashboardSummaryResponse, DashboardTrendPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _base_runs_query(db: Session, user_id: int):
    return db.query(TestCaseResult, APITestCase, Project).join(APITestCase, APITestCase.id == TestCaseResult.test_case_id).join(Project, Project.id == APITestCase.project_id).filter(Project.owner_id == user_id)


@router.get("/recent-runs", response_model=list[DashboardRecentRun])
def recent_runs(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = _base_runs_query(db, current_user.id).order_by(TestCaseResult.created_at.desc()).limit(max(1, min(limit, 50))).all()
    return [DashboardRecentRun(id=r.id, test_case_id=r.test_case_id, project_name=p.name, status=r.status, actual_response_time_ms=r.actual_response_time_ms, created_at=r.created_at) for r, _, p in rows]


@router.get("/failures", response_model=list[DashboardFailure])
def recent_failures(limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = _base_runs_query(db, current_user.id).filter(TestCaseResult.status == "failed").order_by(TestCaseResult.created_at.desc()).limit(max(1, min(limit, 50))).all()
    return [DashboardFailure(id=r.id, test_case_id=r.test_case_id, project_name=p.name, failure_reason=r.failure_reason, created_at=r.created_at) for r, _, p in rows]


@router.get("/pass-rate")
def pass_rate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total, passed = db.query(func.count(TestCaseResult.id), func.sum(case((TestCaseResult.status == "passed", 1), else_=0))).join(APITestCase, APITestCase.id == TestCaseResult.test_case_id).join(Project, Project.id == APITestCase.project_id).filter(Project.owner_id == current_user.id).one()
    total = total or 0
    passed = passed or 0
    return {"total_runs": total, "passed_runs": passed, "pass_rate": round((passed / total) * 100, 2) if total else 0.0}


@router.get("/summary", response_model=DashboardSummaryResponse)
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_projects = db.query(func.count(Project.id)).filter(Project.owner_id == current_user.id).scalar() or 0
    total_test_cases = db.query(func.count(APITestCase.id)).join(Project, Project.id == APITestCase.project_id).filter(Project.owner_id == current_user.id).scalar() or 0
    total_test_suites = db.query(func.count(TestSuite.id)).join(Project, Project.id == TestSuite.project_id).filter(Project.owner_id == current_user.id).scalar() or 0

    total_runs, passed_runs, failed_runs, avg_rt = db.query(
        func.count(TestCaseResult.id),
        func.sum(case((TestCaseResult.status == "passed", 1), else_=0)),
        func.sum(case((TestCaseResult.status == "failed", 1), else_=0)),
        func.avg(TestCaseResult.actual_response_time_ms),
    ).join(APITestCase, APITestCase.id == TestCaseResult.test_case_id).join(Project, Project.id == APITestCase.project_id).filter(Project.owner_id == current_user.id).one()

    latest_runs = recent_runs(5, db, current_user)
    failures = recent_failures(5, db, current_user)

    recent_project = db.query(Project.name).filter(Project.owner_id == current_user.id).order_by(Project.id.desc()).first()

    trend: list[DashboardTrendPoint] = []
    for i in range(6, -1, -1):
        day = date.today() - timedelta(days=i)
        rows = _base_runs_query(db, current_user.id).filter(func.date(TestCaseResult.created_at) == day.isoformat()).all()
        pcount = sum(1 for r, _, _ in rows if r.status == "passed")
        fcount = sum(1 for r, _, _ in rows if r.status == "failed")
        trend.append(DashboardTrendPoint(date=day.isoformat(), passed=pcount, failed=fcount))

    total_runs = total_runs or 0
    passed_runs = passed_runs or 0
    failed_runs = failed_runs or 0
    return DashboardSummaryResponse(
        total_projects=total_projects,
        total_test_cases=total_test_cases,
        total_test_suites=total_test_suites,
        total_test_runs=total_runs,
        total_passed_runs=passed_runs,
        total_failed_runs=failed_runs,
        overall_pass_rate=round((passed_runs / total_runs) * 100, 2) if total_runs else 0.0,
        average_response_time_ms=round(avg_rt, 2) if avg_rt is not None else None,
        most_recently_updated_project=recent_project[0] if recent_project else None,
        trend=trend,
        latest_test_runs=latest_runs,
        latest_failed_tests=failures,
    )
