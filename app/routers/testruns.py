from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models import APITestCase, Project, TestCaseResult, TestSuite, TestSuiteRun, User
from app.schemas.test_run import TestCaseResultResponse, TestSuiteRunResponse
from app.services.test_execution_service import execute_test_case

router = APIRouter(tags=["Test Runs"])


def _owned_test_case(db: Session, test_case_id: int, user_id: int) -> APITestCase:
    test_case = db.query(APITestCase).join(Project, Project.id == APITestCase.project_id).filter(APITestCase.id == test_case_id, Project.owner_id == user_id).first()
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


def _owned_suite(db: Session, suite_id: int, user_id: int) -> TestSuite:
    suite = db.query(TestSuite).join(Project, Project.id == TestSuite.project_id).filter(TestSuite.id == suite_id, Project.owner_id == user_id).first()
    if suite is None:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return suite


@router.post("/test-cases/{test_case_id}/run", response_model=TestCaseResultResponse, status_code=201)
def run_test_case(test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    test_case = _owned_test_case(db, test_case_id, current_user.id)
    result = TestCaseResult(test_case_id=test_case.id, suite_run_id=None, **execute_test_case(test_case))
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/test-cases/{test_case_id}/runs", response_model=list[TestCaseResultResponse])
def list_test_case_runs(test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _owned_test_case(db, test_case_id, current_user.id)
    return db.query(TestCaseResult).filter(TestCaseResult.test_case_id == test_case_id).order_by(TestCaseResult.created_at.desc()).all()


@router.post("/test-suites/{suite_id}/run", response_model=TestSuiteRunResponse, status_code=201)
def run_test_suite(suite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suite = _owned_suite(db, suite_id, current_user.id)
    if not suite.test_cases:
        raise HTTPException(status_code=400, detail="Cannot run an empty test suite")

    started = perf_counter()
    suite_run = TestSuiteRun(suite_id=suite.id, status="passed", total_tests=len(suite.test_cases), passed_count=0, failed_count=0, total_duration_ms=0)
    db.add(suite_run)
    db.flush()

    for test_case in suite.test_cases:
        execution = execute_test_case(test_case)
        result = TestCaseResult(test_case_id=test_case.id, suite_run_id=suite_run.id, **execution)
        if execution["status"] == "passed":
            suite_run.passed_count += 1
        else:
            suite_run.failed_count += 1
            suite_run.status = "failed"
        db.add(result)

    suite_run.total_duration_ms = (perf_counter() - started) * 1000
    suite_run.summary = f"{suite_run.passed_count} passed, {suite_run.failed_count} failed"
    db.commit()
    db.refresh(suite_run)
    return suite_run


@router.get("/test-suites/{suite_id}/runs", response_model=list[TestSuiteRunResponse])
def list_suite_runs(suite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _owned_suite(db, suite_id, current_user.id)
    return db.query(TestSuiteRun).filter(TestSuiteRun.suite_id == suite_id).order_by(TestSuiteRun.created_at.desc()).all()


@router.get("/test-runs", response_model=list[TestCaseResultResponse])
def list_all_test_runs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(TestCaseResult).join(APITestCase, APITestCase.id == TestCaseResult.test_case_id).join(Project, Project.id == APITestCase.project_id).filter(Project.owner_id == current_user.id).order_by(TestCaseResult.created_at.desc()).all()


@router.get("/test-runs/{run_id}", response_model=TestCaseResultResponse)
def get_test_run(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    run = db.query(TestCaseResult).join(APITestCase, APITestCase.id == TestCaseResult.test_case_id).join(Project, Project.id == APITestCase.project_id).filter(TestCaseResult.id == run_id, Project.owner_id == current_user.id).first()
    if run is None:
        raise HTTPException(status_code=404, detail="Test run not found")
    return run
