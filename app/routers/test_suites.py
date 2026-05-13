from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.api_test_case import APITestCase
from app.models.project import Project
from app.models.test_suite import TestSuite
from app.models.user import User
from app.schemas.test_suite import TestSuiteCreate, TestSuiteResponse, TestSuiteUpdate

router = APIRouter(tags=["Test Suites"])


def _ensure_project(db: Session, project_id: int, user_id: int) -> None:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")


def _owned_suite(db: Session, suite_id: int, user_id: int) -> TestSuite:
    suite = db.query(TestSuite).join(Project, Project.id == TestSuite.project_id).filter(TestSuite.id == suite_id, Project.owner_id == user_id).first()
    if suite is None:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return suite


def _serialize_suite(suite: TestSuite) -> TestSuiteResponse:
    return TestSuiteResponse.model_validate({**suite.__dict__, "test_case_ids": [case.id for case in suite.test_cases]})


@router.post("/projects/{project_id}/test-suites", response_model=TestSuiteResponse, status_code=201)
def create_test_suite(project_id: int, payload: TestSuiteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_project(db, project_id, current_user.id)
    suite = TestSuite(project_id=project_id, **payload.model_dump())
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return _serialize_suite(suite)


@router.get("/projects/{project_id}/test-suites", response_model=list[TestSuiteResponse])
def list_test_suites(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_project(db, project_id, current_user.id)
    suites = db.query(TestSuite).filter(TestSuite.project_id == project_id).all()
    return [_serialize_suite(suite) for suite in suites]


@router.get("/test-suites/{suite_id}", response_model=TestSuiteResponse)
def get_test_suite(suite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _serialize_suite(_owned_suite(db, suite_id, current_user.id))


@router.put("/test-suites/{suite_id}", response_model=TestSuiteResponse)
def update_test_suite(suite_id: int, payload: TestSuiteUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suite = _owned_suite(db, suite_id, current_user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(suite, key, value)
    db.commit()
    db.refresh(suite)
    return _serialize_suite(suite)


@router.delete("/test-suites/{suite_id}", status_code=204)
def delete_test_suite(suite_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suite = _owned_suite(db, suite_id, current_user.id)
    db.delete(suite)
    db.commit()


@router.post("/test-suites/{suite_id}/test-cases/{test_case_id}", response_model=TestSuiteResponse)
def add_test_case_to_suite(suite_id: int, test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suite = _owned_suite(db, suite_id, current_user.id)
    test_case = db.query(APITestCase).filter(APITestCase.id == test_case_id, APITestCase.project_id == suite.project_id).first()
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    if test_case not in suite.test_cases:
        suite.test_cases.append(test_case)
        db.commit()
        db.refresh(suite)
    return _serialize_suite(suite)


@router.delete("/test-suites/{suite_id}/test-cases/{test_case_id}", response_model=TestSuiteResponse)
def remove_test_case_from_suite(suite_id: int, test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suite = _owned_suite(db, suite_id, current_user.id)
    test_case = db.query(APITestCase).filter(APITestCase.id == test_case_id, APITestCase.project_id == suite.project_id).first()
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    if test_case in suite.test_cases:
        suite.test_cases.remove(test_case)
        db.commit()
        db.refresh(suite)
    return _serialize_suite(suite)
