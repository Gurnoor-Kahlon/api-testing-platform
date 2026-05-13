from pydantic import BaseModel, ConfigDict, Field


class TestSuiteBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)


class TestSuiteResponse(TestSuiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: object
    updated_at: object
    test_case_ids: list[int] = []
