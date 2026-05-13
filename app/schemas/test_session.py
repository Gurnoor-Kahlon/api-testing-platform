from datetime import datetime

from pydantic import BaseModel


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
