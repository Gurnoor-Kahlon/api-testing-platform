from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


test_suite_cases = Table(
    "test_suite_cases",
    Base.metadata,
    Column("suite_id", Integer, ForeignKey("test_suites.id", ondelete="CASCADE"), primary_key=True),
    Column("test_case_id", Integer, ForeignKey("api_test_cases.id", ondelete="CASCADE"), primary_key=True),
)


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="test_suites")
    test_cases = relationship("APITestCase", secondary=test_suite_cases, back_populates="suites")
