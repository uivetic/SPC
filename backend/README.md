# SPC Backend API

FastAPI backend za Sistem Praćenja Članstva web aplikaciju.

## Setup

1. Instaliraj dependencies:
```bash
pip install -r requirements.txt
```

2. Kopiraj `.env.example` u `.env` i popuni vrednosti:
```bash
cp .env.example .env
```

3. Pokreni server:
```bash
uvicorn app.main:app --reload
```

Server će biti dostupan na `http://localhost:8000`

API dokumentacija: `http://localhost:8000/docs`

## Environment Variables

- `GOOGLE_CLIENT_ID` - Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth Client Secret
- `GOOGLE_REDIRECT_URI` - OAuth redirect URI
- `JWT_SECRET_KEY` - Secret key za JWT token signing
- `GOOGLE_SHEETS_CREDENTIALS_PATH` - Path do credentials.json fajla
- `GOOGLE_SHEETS_ID` - Google Sheets document ID
- `FRONTEND_URL` - Frontend URL za CORS
- `REDIS_URL` - Redis connection URL (opciono)

## API Endpoints

- `GET /api/v1/auth/google` - Get Google OAuth URL
- `GET /api/v1/auth/google/callback` - OAuth callback handler
- `GET /api/v1/auth/me` - Get current user (protected)
- `POST /api/v1/auth/logout` - Logout (protected)
- `POST /api/v1/points/write` - Write points (protected)
- `GET /api/v1/points/{name}` - Get points for person (protected)
- `GET /api/v1/points/all` - Get all people with points (protected)
- `GET /api/v1/users` - Get all users (protected)
- `GET /api/v1/users/search?q={query}` - Search users (protected)
- `GET /api/v1/sheets/activities` - Get activities (protected)
- `GET /api/v1/sheets/projects` - Get projects (protected)

