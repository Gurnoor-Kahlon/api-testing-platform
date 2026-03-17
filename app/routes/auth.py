from fastapi import APIRouter, HTTPException
from app.schemas import LoginRequest, TokenResponse
from app.auth import authenticate_user, create_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "access_token": create_token(),
        "token_type": "bearer"
    }