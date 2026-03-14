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

## Testing & Reliability

The project implements a **multi-layered testing strategy** to ensure that game logic, state management, and cross-platform determinism are maintained across the full stack.

### 1. Mathematical Game Engine Integrity
The core "Arithmetic Merge" logic is verified for absolute correctness, ensuring the game behaves exactly as designed under all conditions.
- **Deterministic Move Resolution:** Every tile slide, merge, and spawn logic has been verified against a 788-move canonical game state.
- **Floating-Point RNG Parity:** The random number generation (RNG) is synchronized with 10-decimal-point precision across the JavaScript and Python environments, ensuring identical game seeds yield identical results.
- **Complex Grid Transitions:** Tested edge cases for grid merges, including multi-tile collapses and "stuck" game states.

### 2. Session & Persistence Reliability
We ensure that user progress and statistics are never lost, even across different browser sessions or network environments.
- **Auto-Recovery (Cache Miss):** Verified that the system detects empty sessionStorage (common in tab refreshes) and automatically restores statistics from the server using the existing session identifier.
- **Session Integrity:** Confirmed that game outcomes (wins, losses, and abandoned games) are accurately synchronized with the backend database, ensuring statistics remain consistent even if the local browser cache is cleared.
- **Storage Resilience:** Features a "fail-safe" mechanism that allows the game to remain playable in restricted environments (e.g., strict Incognito Mode) where local writes are blocked, by defaulting to memory-only state management.

### 3. Backend-Enforced Security & Rules
The connection between the UI and the server is hardened to prevent cheating and ensure fair play.
- **Move Verification:** Every game is replayed and verified on the server. The tests confirm the backend correctly rejects invalid move sequences or forged scores.
- **Rate-Limit Enforcement:** Verified that the system correctly manages high-frequency requests (e.g., spamming the restart button) to maintain server stability.
- **Auth-Linked Telemetry:** Confirmed that all statistics updates are securely linked to persistent user sessions using `credentials: 'include'`.

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

- **Replay Attack Vulnerability**
    - **Issue:** A user could theoretically submit the same winning game sequence multiple times to inflate statistics.
    - **Planned Fix:** Implementation of server-generated game session IDs issued at the start of each game. These IDs will be stored in the database and marked as "consumed" upon verification to ensure each game can only be submitted once.

- **UI/UX Testing Scope**
    - **Limitation:** While the core game engine, RNG parity, and context logic are strictly tested via Jest, pure UI/UX components (visual styling, layout shifts, and animations) are not currently covered.

- **Session-Scoped Persistence**
    - **Behavior:** Statistics and progress are currently tied to a **unique session identifier** stored in browser cookies/session state.
    - **Limitation:** User data does not persist across different browsers or devices (e.g., progress does not sync between desktop and mobile).
    - **Trade-off:** This design prioritizes a "zero-friction" user experience, allowing players to engage immediately without the friction of a mandatory OAuth or registration wall.

- **Temporal vs. Reactive UI Locking**
    - **Behavior:** The 'Restart' button utilizes a fixed 10-second temporal lockout (via `setTimeout`) to discourage spamming, aligning with the backend rate-limit window.
    - **Limitation:** The lockout is independent of the network request lifecycle; it does not "react" to the API response but instead enforces a blind cooldown.
    - **Mitigation:** System integrity is maintained via **Backend Rate Limiting** (10-second window for restart/verify), following a "Security-in-Depth" philosophy where the server acts as the final arbiter of truth.

- **Client-Side Storage Volatility**
    - **Behavior:** The application utilizes `sessionStorage` for low-latency statistics display.
    - **Limitation:** In environments with strict privacy settings or "private/incognito" modes, storage writes may fail.
    - **Resilience:** The system implements a fallback to in-memory state, ensuring the game remains fully playable even when persistence is unavailable.

- **Deterministic Replay Scope**
    - **Behavior:** RNG parity is strictly verified for the primary game loop, move resolution, and tile generation.
    - **Limitation:** Certain UI-only visual animations or non-critical secondary effects are not included in the deterministic seed synchronization, as they do not impact game state integrity.
