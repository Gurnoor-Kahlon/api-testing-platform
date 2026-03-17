from fastapi import Header, HTTPException

DEMO_USER = {
    "username": "admin",
    "password": "password123"
}

VALID_TOKEN = "testtoken123"


def authenticate_user(username: str, password: str) -> bool:
    return username == DEMO_USER["username"] and password == DEMO_USER["password"]


def create_token() -> str:
    return VALID_TOKEN


def verify_token(authorization: str = Header(default=None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    expected_value = f"Bearer {VALID_TOKEN}"
    if authorization != expected_value:
        raise HTTPException(status_code=401, detail="Invalid or expired token")