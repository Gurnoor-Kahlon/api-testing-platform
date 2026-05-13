# API Testing Platform

A full-stack automated API testing platform that helps teams create API test cases, organize suites, execute tests, and track quality trends over time.

## Why This Project Exists
Modern backend teams need a lightweight way to validate API behavior quickly. This project demonstrates how to build a production-oriented developer tool with end-to-end workflows across API design, persistence, frontend UX, automated testing, and CI.

## Key Features
- JWT authentication and user-scoped data access.
- Project CRUD for test organization.
- API test case CRUD with assertion metadata.
- Test suite CRUD and suite membership management.
- Test execution engine for single test cases and full suites.
- Dashboard analytics for pass rate, recent runs, and failures.
- Persistent run history for tracking regressions.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, pytest, httpx
- **Frontend:** React, TypeScript, Vite, Chart.js
- **DevOps:** Docker, Docker Compose, GitHub Actions

## Architecture Overview
```text
React (Vite)
   |
   v
FastAPI routers -> services -> repositories -> PostgreSQL
   |
   v
Test execution engine (httpx) -> run results -> dashboard analytics
```

Backend packages are grouped by concern in `app/core`, `app/db`, `app/models`, `app/schemas`, `app/routers`, `app/services`, and `app/repositories`.

## Screenshots
Use real screenshots from your local environment:
- Login page
- Dashboard summary cards
- Recent runs + failures feed

> Do not add mockups or generated UI screenshots.

## Local Setup
### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker Setup
```bash
cp .env.docker.example .env.docker
docker compose up --build
```

Services:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Selenium: `http://localhost:4444`

Stop services:
```bash
docker compose down
```

## Environment Variables
### Local development (`.env.local`)
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tasks_db`
- `BACKEND_URL=http://localhost:8000`
- `FRONTEND_URL=http://localhost:5173`
- `VITE_API_BASE_URL=http://localhost:8000`

### Docker development (`.env.docker`)
- `DATABASE_URL=postgresql://postgres:postgres@db:5432/tasks_db`
- `BACKEND_URL=http://api:8000`
- `FRONTEND_URL=http://frontend:5173`
- `SELENIUM_URL=http://selenium:4444`

## Running Tests
```bash
pytest
```

## API Examples
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","full_name":"Dev User","password":"SecurePass123"}'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"SecurePass123"}'
```

Protected examples:
- `POST /projects/{project_id}/test-cases`
- `POST /test-cases/{id}/run`
- `POST /test-suites/{id}/run`
- `GET /dashboard/summary`

## GitHub Actions / CI
On every pull request to `main`, CI runs:
- Backend pytest suite with PostgreSQL service
- Frontend lint (`npm run lint`)
- Frontend build (`npm run build`)
- Dependency caching for pip and npm installs

Workflow file: `.github/workflows/ci.yml`.

## Project Structure
```text
app/
  core/ db/ models/ repositories/ routers/ schemas/ services/
frontend/
tests/
alembic/
.github/workflows/
```

## Demo Workflow
1. Register and login.
2. Create a project.
3. Add API test cases.
4. Create a test suite and attach test cases.
5. Execute test case or suite runs.
6. Review dashboard metrics and failure trends.

## Development Workflow
- Create focused feature branches.
- Keep PRs small and reviewable.
- Use Conventional Commits.
- Add/update tests for backend changes.
- Update docs when behavior changes.

See `CONTRIBUTING.md` for full contribution and PR guidance.

## Troubleshooting
- **Database connection issues:** verify `DATABASE_URL` and confirm PostgreSQL is running.
- **Frontend cannot reach API:** verify `VITE_API_BASE_URL` and backend port mapping.
- **Docker startup errors:** ensure `.env.docker` exists and ports 5432/5173/8000 are free.

## Future Improvements
- Background job queue for long-running suite execution.
- Additional assertion operators (regex, contains, ranges, array checks).
- Rich run-history filtering and trend visualization.
- Role-based collaboration for team projects.

## Resume Bullet Points
- Built a full-stack automated API testing platform using FastAPI, React/TypeScript, PostgreSQL, Docker, and pytest, enabling users to create API test cases, execute test suites, and review pass/fail history in a dashboard.
- Implemented an API test execution engine with `httpx`, assertion validation, test run history, JWT auth, and pull-request CI workflows in GitHub Actions.
- Containerized backend, frontend, and database services with Docker Compose and documented local + containerized workflows for reproducible development.

## What I Learned
- Designing API-first systems with clear schema and service boundaries.
- Building trustworthy automation with repeatable tests and CI.
- Translating engineering work into clear documentation and portfolio-ready project narratives.
