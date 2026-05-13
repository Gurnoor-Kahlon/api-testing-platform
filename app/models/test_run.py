from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class TestSuiteRun(Base):
    __tablename__ = "test_suite_runs"

    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    total_tests = Column(Integer, nullable=False)
    passed_count = Column(Integer, nullable=False)
    failed_count = Column(Integer, nullable=False)
    total_duration_ms = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    suite = relationship("TestSuite")
    results = relationship("TestCaseResult", back_populates="suite_run", cascade="all, delete-orphan")


class TestCaseResult(Base):
    __tablename__ = "test_case_results"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("api_test_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    suite_run_id = Column(Integer, ForeignKey("test_suite_runs.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(String(20), nullable=False)
    failure_reason = Column(Text, nullable=True)
    actual_status_code = Column(Integer, nullable=True)
    actual_response_time_ms = Column(Float, nullable=True)
    response_preview = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    test_case = relationship("APITestCase")
    suite_run = relationship("TestSuiteRun", back_populates="results")
