from sqlalchemy import Boolean, Column, Integer, String

from app.db.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(300), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
