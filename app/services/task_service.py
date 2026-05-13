from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)

    def list_tasks(self):
        return self.repo.list()

    def get_task(self, task_id: int):
        task = self.repo.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def create_task(self, payload: TaskCreate):
        return self.repo.create(payload)

    def update_task(self, task_id: int, payload: TaskUpdate):
        task = self.get_task(task_id)
        return self.repo.update(task, payload)

    def delete_task(self, task_id: int):
        task = self.get_task(task_id)
        deleted_task_id = self.repo.delete(task)
        return {"message": "Task deleted", "task": {"id": deleted_task_id}}
