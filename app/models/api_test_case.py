from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class APITestCase(Base):
    __tablename__ = "api_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    http_method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(JSON, nullable=True)
    query_params = Column(JSON, nullable=True)
    request_body = Column(JSON, nullable=True)
    expected_status_code = Column(Integer, nullable=False)
    expected_response_time_ms = Column(Integer, nullable=False)
    expected_json_field = Column(String(255), nullable=True)
    expected_json_value = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="test_cases")
    suites = relationship("TestSuite", secondary="test_suite_cases", back_populates="test_cases")
