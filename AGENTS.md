# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview

SPC (Sistem Praćenja Članstva) — a membership tracking and points management app for a Serbian BEST organization. Two-service monorepo: Python FastAPI backend + React/Vite/TypeScript frontend.

### Services

| Service | Port | Start Command |
|---------|------|---------------|
| Backend | 8000 | `cd backend && source ../venv/bin/activate && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| Frontend | 5173 | `cd frontend && npx vite --host 0.0.0.0 --port 5173` |

### Secrets / Environment Variables

The following secrets must be configured (injected as environment variables by Cursor Cloud):
- `GOOGLE_CLIENT_ID` — Google OAuth 2.0 client ID
- `GOOGLE_CLIENT_SECRET` — Google OAuth 2.0 client secret
- `GOOGLE_SHEETS_ID` — ID of the Google Sheet used for membership data

On startup, generate `backend/.env` and `frontend/.env.local` from these env vars. See `backend/.env.example` and `frontend/.env.example` for the full template. A `service-account-key.json` is also needed at `backend/service-account-key.json` for Google Sheets API write access (not currently available as a secret).

### Development Notes

- **Backend venv**: The virtualenv lives at `/workspace/venv`. Always activate it before running backend commands.
- **python3.12-venv**: The system package `python3.12-venv` must be installed to create the venv (`sudo apt-get install -y python3.12-venv`).
- **Backend .env**: Must exist at `backend/.env`. Generate it from env vars or copy from `backend/.env.example`. The app starts fine with placeholder Google OAuth credentials — health and root endpoints work, but auth/sheets/groups require real credentials.
- **Frontend .env.local**: Must exist at `frontend/.env.local` with `VITE_API_URL=http://localhost:8000` and `VITE_GOOGLE_CLIENT_ID`.
- **Redis**: Optional. The backend degrades gracefully without Redis — no caching, but all features still work.
- **No database**: All data is stored in Google Sheets (external service).
- **ESLint**: The `eslint.config.js` uses ESLint 9 flat config format. The `npm run lint` script in `package.json` uses the legacy `--ext` flag which is incompatible — run `npx eslint .` instead. There are pre-existing lint errors in the codebase (11 as of this writing).
- **No automated tests**: The codebase does not include test files or test frameworks.
- **Build**: `cd frontend && npm run build` runs TypeScript compilation + Vite build.
- **API docs**: Available at `http://localhost:8000/docs` (Swagger UI) when backend is running.
