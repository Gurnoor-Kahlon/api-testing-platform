from datetime import datetime
from typing import Literal

from pydantic import BaseModel


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
