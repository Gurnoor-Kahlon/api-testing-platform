import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390000)
    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, hash_hex = password_hash.split(":", maxsplit=1)
    candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 390000)
    return hmac.compare_digest(candidate_hash, bytes.fromhex(hash_hex))


def create_access_token(user_id: int, expires_minutes: int = 60) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode("utf-8"))
    payload = _b64url_encode(json.dumps({"sub": str(user_id), "exp": int((datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).timestamp())}, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header}.{payload}".encode("utf-8")
    signature = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64url_encode(signature)}"


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme), db: Session = Depends(get_db)) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        header, payload, signature = credentials.credentials.split(".")
        signing_input = f"{header}.{payload}".encode("utf-8")
        expected = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(signature)):
            raise ValueError
        decoded = json.loads(_b64url_decode(payload))
        if int(decoded["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError
        user_id = int(decoded["sub"])
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme), db: Session = Depends(get_db)):
    get_current_user(credentials, db)
