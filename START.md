# Kako pokrenuti SPC Web App

## Brzo pokretanje

### 1. Backend (Terminal 1)

```bash
cd backend

# Aktiviraj virtual environment (ako već nije aktiviran)
source ../venv/bin/activate

# Proveri da li .env fajl postoji i ima sve vrednosti
cat .env

# Pokreni backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend će biti dostupan na: **http://localhost:8000**
API dokumentacija: **http://localhost:8000/docs**

### 2. Frontend (Terminal 2)

```bash
cd frontend

# Proveri da li .env fajl postoji
cat .env

# Pokreni frontend development server
npm run dev
```

Frontend će biti dostupan na: **http://localhost:5173**

## Provera konfiguracije

### Backend `.env` fajl treba da sadrži:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=../credentials.json
GOOGLE_SHEETS_ID=17yR3BJzslf4HLMGTDc0OvzRaY3t7VAZ1-CGx5GxQM_Q

# Redis (opciono)
REDIS_URL=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://localhost:5173

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend `.env` fajl treba da sadrži:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Troubleshooting

### Backend ne startuje

1. Proveri da li su sve dependencies instalirane:
   ```bash
   pip list | grep -E "(fastapi|uvicorn|pydantic|gspread)"
   ```

2. Proveri da li `credentials.json` postoji na putanji iz `.env`:
   ```bash
   ls -la ../credentials.json
   ```

3. Proveri logove za greške u terminalu gde pokrećeš backend

### Frontend ne startuje

1. Proveri da li su dependencies instalirane:
   ```bash
   npm list --depth=0
   ```

2. Ako ima problema, reinstaliraj:
   ```bash
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

### CORS greške

- Proveri da li je `BACKEND_CORS_ORIGINS` u backend `.env` uključuje `http://localhost:5173`
- Proveri da li je `FRONTEND_URL` u backend `.env` postavljen na `http://localhost:5173`

### Google OAuth ne radi

1. Idite na [Google Cloud Console](https://console.cloud.google.com/)
2. Kreirajte OAuth 2.0 Client ID
3. Dodajte Authorized redirect URI: `http://localhost:5173/auth/callback`
4. Kopirajte Client ID i Secret u oba `.env` fajla

## Testiranje

1. Otvorite browser: http://localhost:5173
2. Kliknite "Sign in with Google"
3. Prijavite se
4. Bićete preusmereni na Dashboard

## Korisne komande

### Backend
```bash
# Pokreni server
uvicorn app.main:app --reload

# Pokreni na specifičnom portu
uvicorn app.main:app --reload --port 8000

# Pokreni bez reload-a (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Development server
npm run dev

# Build za production
npm run build

# Preview production build
npm run preview
```

