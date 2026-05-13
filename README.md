# Automated API Testing Platform

A full-stack learning project for building a professional automated API testing platform with FastAPI, React, Docker, and CI.

## Current Scope
- FastAPI backend with auth, task management, test run tracking, and test session endpoints.
- React + Vite frontend scaffold.
- Automated backend test suite with pytest.
- Docker Compose setup for API + PostgreSQL + Selenium.
- GitHub Actions workflow running tests on pull requests and pushes to `main`.

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL, pytest
- **Frontend:** React, TypeScript, Vite
- **DevOps:** Docker, Docker Compose, GitHub Actions

## Local Setup (Backend)
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your local env file from the template:
   ```bash
   cp .env.example .env.local
   ```
4. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```
5. API runs at `http://localhost:8000`.

## Local Setup (Frontend)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.

## Docker Setup
1. Create docker env file:
   ```bash
   cp .env.docker.example .env.docker
   ```
2. Start services:
   ```bash
   docker-compose up --build
   ```
3. Stop services:
   ```bash
   docker-compose down
   ```

## Testing
Run backend tests:
```bash
pytest
```

## Security Notes
- Never commit real secrets or `.env` files.
- Use `.env.example` and `.env.docker.example` for safe defaults only.

## Planned Improvements
- Replace demo token auth with JWT + hashed passwords.
- Add project/suite/test-case domain models.
- Add structured test execution pipeline and historical analytics dashboard.
- Expand frontend beyond scaffold to full product UI.
