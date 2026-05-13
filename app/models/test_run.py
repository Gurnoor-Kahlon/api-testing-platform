from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.database import Base


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(100), nullable=False)
    test_type = Column(String(20), nullable=False, default="api")
    status = Column(String(50), nullable=False)
    result = Column(String(1000), nullable=True)
    execution_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
