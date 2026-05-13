from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(verify_token)])


@router.get("", response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)):
    return TaskService(db).list_tasks()


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return TaskService(db).get_task(task_id)


@router.post("", response_model=Task, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return TaskService(db).create_task(task)


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate, db: Session = Depends(get_db)):
    return TaskService(db).update_task(task_id, updated_task)


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return TaskService(db).delete_task(task_id)
