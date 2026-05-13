from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


class APITestCaseBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    http_method: str
    url: HttpUrl
    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    request_body: dict[str, Any] | list[Any] | None = None
    expected_status_code: int = Field(ge=100, le=599)
    expected_response_time_ms: int = Field(gt=0, le=120000)
    expected_json_field: str | None = Field(default=None, max_length=255)
    expected_json_value: str | None = Field(default=None, max_length=2000)

    @field_validator("http_method")
    @classmethod
    def validate_http_method(cls, value: str) -> str:
        method = value.upper().strip()
        if method not in _ALLOWED_METHODS:
            raise ValueError("Invalid HTTP method")
        return method


class APITestCaseCreate(APITestCaseBase):
    pass


class APITestCaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    http_method: str | None = None
    url: HttpUrl | None = None
    headers: dict[str, str] | None = None
    query_params: dict[str, str] | None = None
    request_body: dict[str, Any] | list[Any] | None = None
    expected_status_code: int | None = Field(default=None, ge=100, le=599)
    expected_response_time_ms: int | None = Field(default=None, gt=0, le=120000)
    expected_json_field: str | None = Field(default=None, max_length=255)
    expected_json_value: str | None = Field(default=None, max_length=2000)

    @field_validator("http_method")
    @classmethod
    def validate_http_method(cls, value: str | None) -> str | None:
        if value is None:
            return None
        method = value.upper().strip()
        if method not in _ALLOWED_METHODS:
            raise ValueError("Invalid HTTP method")
        return method


class APITestCaseResponse(APITestCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: object
    updated_at: object
