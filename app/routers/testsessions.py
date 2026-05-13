import subprocess
import threading
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import SessionLocal, get_db
from app.models import TestSession
from app.schemas.test_session import TestSessionResponse

router = APIRouter(prefix="/test-sessions", tags=["Test Sessions"], dependencies=[Depends(verify_token)])

def run_tests_in_background(session_id: str):
    db = SessionLocal()
    try:
        session = db.query(TestSession).filter(TestSession.id == session_id).first()
        if not session:
            return
        session.status = "running"
        session.started_at = datetime.utcnow()
        db.commit()
        result = subprocess.run(["pytest", "tests/test_testruns.py", "tests/test_tasks.py", "tests/test_auth.py", "tests/test_main.py", "tests/selenium/test_login_ui.py"], capture_output=True, text=True)
        session.status = "completed"
        session.finished_at = datetime.utcnow()
        session.return_code = result.returncode
        session.stdout = result.stdout
        session.stderr = result.stderr
        db.commit()
    except Exception as e:
        session = db.query(TestSession).filter(TestSession.id == session_id).first()
        if session:
            session.status = "failed"
            session.finished_at = datetime.utcnow()
            session.return_code = -1
            session.stdout = ""
            session.stderr = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/run-all")
def run_all_tests(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    db.add(TestSession(id=session_id, status="queued", stdout="", stderr=""))
    db.commit()
    threading.Thread(target=run_tests_in_background, args=(session_id,)).start()
    return {"message": "Test run started", "session_id": session_id}

@router.get("/{session_id}", response_model=TestSessionResponse)
def get_test_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TestSession).filter(TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")
    return session

@router.get("", response_model=list[TestSessionResponse])
def get_all_test_sessions(db: Session = Depends(get_db)):
    return db.query(TestSession).order_by(TestSession.started_at.desc()).all()
