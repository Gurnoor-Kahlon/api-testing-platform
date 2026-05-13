from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class TestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(String(100), primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    return_code = Column(Integer, nullable=True)
    stdout = Column(String(5000), nullable=True)
    stderr = Column(String(5000), nullable=True)
