from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from datetime import datetime
from app.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(300), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(100), nullable=False)
    test_type = Column(String(20), nullable=False, default="api")
    status = Column(String(50), nullable=False)
    result = Column(String(1000), nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(String(100), primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    return_code = Column(Integer, nullable=True)
    stdout = Column(String(5000), nullable=True)
    stderr = Column(String(5000), nullable=True)