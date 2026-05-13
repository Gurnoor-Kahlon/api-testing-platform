from fastapi import APIRouter, HTTPException

from app.core.security import authenticate_user, create_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"access_token": create_token(), "token_type": "bearer"}
