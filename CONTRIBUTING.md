# Contributing Guide

Thanks for your interest in contributing to the API Testing Platform.

## Development Workflow
1. Create a feature branch from `main`.
2. Keep pull requests scoped and reviewable.
3. Follow Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`).
4. Add or update tests for backend changes.
5. Update documentation when behavior or setup changes.

## Local Quality Checks
- Backend tests: `pytest`
- Frontend lint: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`

## Pull Request Checklist
- [ ] Scope is small and focused.
- [ ] Tests were added/updated and pass locally.
- [ ] README/docs were updated for setup or usage changes.
- [ ] No secrets (`.env`, API keys, tokens, credentials) were committed.
- [ ] Planned items are documented under **Planned Improvements**.

## Commit Guidelines
Examples:
- `feat: add suite run history endpoint`
- `test: add coverage for auth token expiry`
- `docs: clarify docker setup for frontend`

Avoid vague messages like `update` or `fixes`.
