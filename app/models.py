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
    result = Column(String(300), nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)