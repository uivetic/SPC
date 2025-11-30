# Quick Start Guide - SPC Web App

## Brzo pokretanje aplikacije

### 1. Backend Setup

```bash
cd backend

# Instaliraj dependencies
pip install -r requirements.txt

# Kreiraj .env fajl
cp .env.example .env

# Otvori .env i popuni:
# - GOOGLE_CLIENT_ID (iz Google Cloud Console)
# - GOOGLE_CLIENT_SECRET (iz Google Cloud Console)  
# - JWT_SECRET_KEY (generiši random string, npr: openssl rand -hex 32)
# - GOOGLE_SHEETS_CREDENTIALS_PATH (putanja do credentials.json, npr: ../credentials.json)

# Pokreni backend
uvicorn app.main:app --reload
```

Backend će biti na: **http://localhost:8000**
API docs: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
# U NOVOM terminalu
cd frontend

# Instaliraj dependencies (već urađeno sa --legacy-peer-deps)
# npm install --legacy-peer-deps

# Kreiraj .env fajl
cp .env.example .env

# Otvori .env i popuni:
# VITE_API_URL=http://localhost:8000
# VITE_GOOGLE_CLIENT_ID=(isti kao GOOGLE_CLIENT_ID u backend .env)

# Pokreni frontend
npm run dev
```

Frontend će biti na: **http://localhost:5173**

### 3. Google OAuth Setup (prvi put)

1. Idite na https://console.cloud.google.com/
2. Kreirajte projekat ili izaberite postojeći
3. Omogućite "Google+ API"
4. Kreirajte OAuth 2.0 Client ID:
   - Application type: **Web application**
   - Name: SPC Web App
   - Authorized redirect URIs: `http://localhost:5173/auth/callback`
5. Kopirajte **Client ID** i **Client Secret**
6. Dodajte ih u oba `.env` fajla

### 4. Testiranje

1. Otvorite browser: http://localhost:5173
2. Kliknite "Sign in with Google"
3. Prijavite se
4. Bićete preusmereni na Dashboard

## Troubleshooting

### Backend ne startuje
- Proverite da li su sve dependencies instalirane: `pip list`
- Proverite da li `.env` fajl postoji i ima sve vrednosti
- Proverite da li `credentials.json` postoji na putanji iz `.env`

### Frontend ne startuje
- Proverite da li su dependencies instalirane: `npm list`
- Proverite da li `.env` fajl postoji
- Proverite konzolu za greške

### OAuth ne radi
- Proverite da li je redirect URI tačan u Google Cloud Console
- Proverite da li su Client ID i Secret ispravni u `.env` fajlovima
- Proverite browser konzolu (F12) za greške

### CORS greške
- Proverite da li je `FRONTEND_URL` u backend `.env` postavljen na `http://localhost:5173`
- Proverite da li je `BACKEND_CORS_ORIGINS` uključuje `http://localhost:5173`

## Korisne komande

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend  
cd frontend
npm run dev

# Build za production
cd frontend
npm run build
```

