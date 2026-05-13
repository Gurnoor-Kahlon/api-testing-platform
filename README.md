# Automated API Testing Platform

A full-stack learning project for building a professional automated API testing platform with FastAPI, React, Docker, and CI.

## Current Scope
- FastAPI backend with auth, project management, API test case management, test suite management, test run tracking, and test session endpoints.
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


## Authentication Flow
- Register with `POST /auth/register` using email, full name, and password.
- Login with `POST /auth/login` to receive a JWT access token.
- Call protected endpoints using `Authorization: Bearer <token>`.
- Get the current user with `GET /auth/me`.

### Example Requests
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","full_name":"Dev User","password":"SecurePass123"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"SecurePass123"}'
```

### Protected Project + Testing Endpoints
- Test Cases: `POST /projects/{project_id}/test-cases`, `GET /projects/{project_id}/test-cases`, `GET /test-cases/{id}`, `PUT /test-cases/{id}`, `DELETE /test-cases/{id}`
- Test Suites: `POST /projects/{project_id}/test-suites`, `GET /projects/{project_id}/test-suites`, `GET /test-suites/{id}`, `PUT /test-suites/{id}`, `DELETE /test-suites/{id}`
- Suite Membership: `POST /test-suites/{suite_id}/test-cases/{test_case_id}`, `DELETE /test-suites/{suite_id}/test-cases/{test_case_id}`

### Protected Project Endpoints
- `POST /projects`
- `GET /projects`
- `GET /projects/{id}`
- `PUT /projects/{id}`
- `DELETE /projects/{id}`

Projects are user-scoped: each user can only access their own project data.

## Security Notes
- Never commit real secrets or `.env` files.
- Use `.env.example` and `.env.docker.example` for safe defaults only.

## Planned Improvements
- Add structured test execution pipeline and historical analytics dashboard.
- Expand frontend beyond scaffold to full product UI.


## Backend Architecture
- Backend modules are organized by concern under `app/core`, `app/db`, `app/models`, `app/schemas`, `app/routers`, `app/services`, and `app/repositories`.
- Legacy imports (`app.database`, `app.models`, `app.schemas`, `app.auth`) remain as compatibility shims while the architecture evolves.

## Database Migrations
- Alembic is configured in `alembic.ini` and `alembic/`.
- Run migrations with:
```bash
alembic upgrade head
```


## Test Execution Engine (Phase 5)

- Run a single test case: `POST /test-cases/{id}/run`
- View single test case run history: `GET /test-cases/{id}/runs`
- Run a full suite: `POST /test-suites/{id}/run`
- View suite run history: `GET /test-suites/{id}/runs`
- View all runs for current user: `GET /test-runs` and `GET /test-runs/{id}`

The execution engine uses `httpx` to send stored requests and validates:
- expected status code
- expected JSON field/value
- response-time threshold

Each run stores pass/fail status, failure reason, actual status code, actual response time, timestamp, and a small response preview.

### Planned Improvements
- Add dedicated frontend pages for run history and suite execution controls.
- Add richer assertion operators (contains, not-equals, regex, array length).
- Add asynchronous/background suite execution for long-running suites.
