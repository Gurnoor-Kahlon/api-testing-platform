from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas import TestRunCreate, TestRunResponse
from app.models import TestRun
from app.database import get_db
from app.auth import verify_token

router = APIRouter(
    prefix="/test-runs",
    tags=["Test Runs"],
    dependencies=[Depends(verify_token)]
)


@router.get("", response_model=list[TestRunResponse])
def get_test_runs(
    status: Optional[str] = None,
    test_type: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TestRun)

    if status:
        query = query.filter(TestRun.status == status)

    if test_type:
        query = query.filter(TestRun.test_type == test_type)

    if sort == "execution_time":
        query = query.order_by(TestRun.execution_time)
    elif sort == "-execution_time":
        query = query.order_by(TestRun.execution_time.desc())
    elif sort == "newest":
        query = query.order_by(TestRun.created_at.desc())
    elif sort == "oldest":
        query = query.order_by(TestRun.created_at.asc())

    return query.all()


@router.get("/stats")
def get_test_run_summary(db: Session = Depends(get_db)):
    total = db.query(TestRun).count()
    passed = db.query(TestRun).filter(TestRun.status == "passed").count()
    failed = db.query(TestRun).filter(TestRun.status == "failed").count()

    return {
        "total": total,
        "passed": passed,
        "failed": failed
    }


@router.post("", response_model=TestRunResponse, status_code=201)
def create_test_run(test_run: TestRunCreate, db: Session = Depends(get_db)):
    new_test_run = TestRun(
        test_name=test_run.test_name,
        test_type=test_run.test_type,
        status=test_run.status,
        result=test_run.result,
        execution_time=test_run.execution_time
    )
    db.add(new_test_run)
    db.commit()
    db.refresh(new_test_run)
    return new_test_run

@router.delete("")
def delete_all_test_runs(db: Session = Depends(get_db)):
    deleted_count = db.query(TestRun).delete()
    db.commit()

    return {
        "message": "All test runs deleted",
        "deleted_count": deleted_count
    }