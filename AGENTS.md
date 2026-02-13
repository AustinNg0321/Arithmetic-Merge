# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: Flask API and game logic.
- `backend/routes/`: HTTP routes (`solo.py`).
- `backend/models/`: SQLAlchemy models.
- `backend/utils/`: core game/util helpers.
- `backend/tests/` and `backend/tests/game_tests/`: pytest suites.
- `backend/static/` and `backend/templates/`: server-rendered assets/templates.
- `frontend/`: Next.js app (App Router).
- `frontend/src/app/`: pages, layouts, and route-specific UI.
- `frontend/public/`: static frontend assets.

## Build, Test, and Development Commands
Run commands from repo root unless noted.

- Backend setup: `python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt pytest`
- Start backend: `python -m backend.app` (serves Flask on `http://localhost:5000`).
- Run backend tests: `pytest backend/tests -q`
- Frontend setup: `cd frontend && npm install`
- Start frontend dev server: `cd frontend && npm run dev` (defaults to `http://localhost:3000`).
- Frontend production build: `cd frontend && npm run build && npm run start`
- Frontend lint: `cd frontend && npm run lint`

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, `snake_case` for functions/variables, `PascalCase` for classes.
- JavaScript/React: follow ESLint (`frontend/eslint.config.mjs`), `camelCase` for vars/functions, `PascalCase` for components.
- Keep route handlers thin; move reusable logic into `backend/utils/`.
- Name tests by behavior, e.g., `test_restart_rate_limiting`.

## Testing Guidelines
- Framework: `pytest` for backend.
- Place tests in `backend/tests/` (or `backend/tests/game_tests/` for engine-level coverage).
- File naming: `test_*.py`; test function naming: `test_*`.
- Prefer small fixtures using `create_app({... "TESTING": True ...})` and validate both status codes and payloads.

## Commit & Pull Request Guidelines
- Keep commit messages short, imperative, and specific (e.g., `Fix tile overflow bug`, `Add rate limiting tests`).
- One logical change per commit.
- PRs should include:
  - Purpose and scope
  - Linked issue (if applicable)
  - Test evidence (`pytest backend/tests -q`, `npm run lint`)
  - Screenshots/GIFs for UI changes in `frontend/`

## Security & Configuration Tips
- Keep secrets in `backend/.env` (do not commit).
- Set `SECRET_KEY` before running backend.
- Default DB is SQLite (`sqlite:///info.db`); use isolated DB settings for tests.
