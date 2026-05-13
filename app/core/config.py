import os
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv('.env')


def _parse_cors_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["http://localhost:5173"]
    return [origin.strip() for origin in raw.split(',') if origin.strip()]


class Settings:
    app_name: str = os.getenv("APP_NAME", "Automated API Testing Platform")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    cors_origins: list[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")


settings = Settings()
