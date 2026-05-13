from sqlalchemy.orm import Session

from app.models import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[TaskModel]:
        return self.db.query(TaskModel).all()

    def get(self, task_id: int) -> TaskModel | None:
        return self.db.query(TaskModel).filter(TaskModel.id == task_id).first()

    def create(self, payload: TaskCreate) -> TaskModel:
        task = TaskModel(title=payload.title, description=payload.description, completed=False)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: TaskModel, payload: TaskUpdate) -> TaskModel:
        task.title = payload.title
        task.description = payload.description
        task.completed = payload.completed
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: TaskModel) -> int:
        task_id = task.id
        self.db.delete(task)
        self.db.commit()
        return task_id
