# Arithmetic Merge

A sliding tile puzzle game inspired by 2048. Combine number and operator tiles arithmetically to create a tile with the value **67**.

🎮 **[Play Live](https://arithmetic-merge.vercel.app)**

This project started as a group project with [@johnliaogithub](https://github.com/johnliaogithub) and [@theCityCR](https://github.com/theCityCR) for the 2025 CSC Project Program. The codebase has since been substantially rewritten with a new backend, and architecture, as well as a modified frontend.

---

## How to Play

Slide tiles up, down, left, or right to combine them. When a number, operator, and number line up (e.g. `3 + 4`), they evaluate into a single tile (`7`). Two new tiles appear after every move.

**Goal:** Create a tile with the value **67**.

### Tile Types

| Tile | Description |
|------|-------------|
| `0`–`9` | Number tiles |
| `+` `-` | Operator tiles |

Note: number tiles generated initially are from 0 to 9, but other number tiles can take any value from -1000 to 1000 inclusive.

### How Tiles Combine

- Empty gaps are removed and tiles collapse toward the slide direction
- When a number, operator, and number are adjacent, they evaluate into a single tile — even if there were gaps between them before collapsing
- Only one operation is evaluated per triplet per move — numbers without an operator between them do not chain (e.g. `1 + 2 3` → `3 3`, not `6`)
- Consecutive identical operators collapse into one (e.g. `+ + +` → `+`)
- Operations are evaluated in the slide direction — left/up evaluates leftmost first, right/down evaluates rightmost first

**Examples:**

| Input | Direction | Output | Reason |
|-------|-----------|--------|--------|
| `1 + 2 + 3` | Left | `3 + 3` | 1+2 evaluated first |
| `1 + 2 + 3` | Right | `1 + 5` | 2+3 evaluated first |
| `5 - 4` | Right | `1` | Always left operand minus right or up minus down |
| `1 + 2 3` | Left | `3 3` | Numbers don't chain without operator |

### Losing Conditions

- No valid moves remain (there are no free spaces and no moves would change the board)
- Any tile exceeds `1000` or drops below `-1000`

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, Tailwind CSS |
| Backend | Flask, SQLAlchemy |
| Database | PostgreSQL |
| Rate Limiting | Redis, flask-limiter |
| Frontend Hosting | Vercel |
| Backend Hosting | Railway |

---

## Features

- **Deterministic seeded RNG** — same seed always produces the same game, enabling server-side verification
- **Server-side game verification** — seed and move list are replayed on the backend to validate outcomes
- **Anonymous session-based user tracking** — via session cookies, no account required
- **User statistics tracking** — wins, losses, and abandoned games
- **sessionStorage caching** — minimizes API requests for fetching statistics
- **localStorage persistence** — game state is preserved across navigation and page refreshes
- **Rate limiting** — all API endpoints are protected against abuse

---

## Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL
- Redis

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the backend:

Linux:
```bash
gunicorn --workers 1 --bind localhost:5000 wsgi:app
```

MacOS:
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES gunicorn --workers 1 --bind localhost:5000 wsgi:app
```

# Windows (WSL recommended, or use waitress)
```bash
waitress-serve --port=5000 backend.wsgi:app
```

After running both the backend and the frontend, open http://localhost:3000 to check out the app.

### Environment Variables

**Frontend** — create `frontend/.env`:

```env
NEXT_PUBLIC_BACKEND_URL="http://localhost:5000"
```

**Backend** — generate a secret key for Flask sessions:

```python
import secrets
print(secrets.token_hex(32))
```

Create `backend/.env` with the generated secret key:

```env
SECRET_KEY="your-secret-key"
DATABASE_URL="postgresql://user:password@localhost:5432/arithmetic_merge"
REDIS_URL="memory://"
FRONTEND_URL="http://localhost:3000"
```

---

## Deployment

- **Frontend** — deployed on Vercel via GitHub integration, auto-deploys on push to `master`
- **Backend** — deployed on Railway with PostgreSQL and Redis plugins
- Set all environment variables in the Railway and Vercel dashboards before deploying

---

## Limitations

- **Replay attack vulnerability** — a user could theoretically submit the same winning game multiple times. Planned fix: server-generated game session IDs issued before each game starts, stored in the database and marked as used after verification to prevent the same game from being submitted multiple times.
- **Anonymous sessions only** — no password-based authentication. Clearing cookies or switching browsers creates a new identity and resets statistics
- **Incomplete test suite** — frontend and backend tests need to be rewritten or added
