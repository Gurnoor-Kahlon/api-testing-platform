from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.api_test_case import APITestCase
from app.models.project import Project
from app.models.user import User
from app.schemas.api_test_case import APITestCaseCreate, APITestCaseResponse, APITestCaseUpdate

router = APIRouter(tags=["Test Cases"])


def _get_owned_project(db: Session, project_id: int, user_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _get_owned_test_case(db: Session, test_case_id: int, user_id: int) -> APITestCase:
    test_case = (
        db.query(APITestCase)
        .join(Project, Project.id == APITestCase.project_id)
        .filter(APITestCase.id == test_case_id, Project.owner_id == user_id)
        .first()
    )
    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.post("/projects/{project_id}/test-cases", response_model=APITestCaseResponse, status_code=201)
def create_test_case(project_id: int, payload: APITestCaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_project(db, project_id, current_user.id)
    data = payload.model_dump()
    data["url"] = str(data["url"])
    test_case = APITestCase(project_id=project_id, **data)
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.get("/projects/{project_id}/test-cases", response_model=list[APITestCaseResponse])
def list_test_cases(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_owned_project(db, project_id, current_user.id)
    return db.query(APITestCase).filter(APITestCase.project_id == project_id).all()


@router.get("/test-cases/{test_case_id}", response_model=APITestCaseResponse)
def get_test_case(test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_owned_test_case(db, test_case_id, current_user.id)


@router.put("/test-cases/{test_case_id}", response_model=APITestCaseResponse)
def update_test_case(test_case_id: int, payload: APITestCaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    test_case = _get_owned_test_case(db, test_case_id, current_user.id)
    updates = payload.model_dump(exclude_unset=True)
    if "url" in updates and updates["url"] is not None:
        updates["url"] = str(updates["url"])
    for key, value in updates.items():
        setattr(test_case, key, value)
    db.commit()
    db.refresh(test_case)
    return test_case


@router.delete("/test-cases/{test_case_id}", status_code=204)
def delete_test_case(test_case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    test_case = _get_owned_test_case(db, test_case_id, current_user.id)
    db.delete(test_case)
    db.commit()
