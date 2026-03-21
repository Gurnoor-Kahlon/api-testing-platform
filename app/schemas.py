from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=300)


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=300)
    completed: bool


class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TestRunCreate(BaseModel):
    test_name: str
    test_type: Literal["api", "ui"] = "api"
    status: Literal["passed", "failed"]
    result: str | None = None
    execution_time: float | None = None


class TestRunResponse(BaseModel):
    id: int
    test_name: str
    test_type: str
    status: str
    result: str | None = None
    execution_time: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class TestSessionResponse(BaseModel):
    id: str
    status: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    return_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None

    class Config:
        from_attributes = True