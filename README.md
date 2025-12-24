# SPC Web App - Sistem Praćenja Članstva

Modern web aplikacija za praćenje članstva i bodova.

## Struktura Projekta

```
SPC/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # Business logic
│   │   ├── utils/    # Utility functions
│   │   └── main.py   # FastAPI app
│   ├── requirements.txt
│   ├── .env          # Environment variables
│   └── service-account-key.json  # Google Service Account credentials
│
└── frontend/         # React frontend
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   └── lib/
    └── package.json
```

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Google Cloud Project sa OAuth credentials
- Google Service Account sa pristupom Google Sheets
- Google Workspace Admin Console pristup (za Domain-Wide Delegation)

### Lokalno Pokretanje

#### Opcija 1: Automatski (preporučeno)

```bash
./start.sh
```

Ova skripta automatski:
- Aktivira virtualno okruženje
- Proverava i instalira pakete ako je potrebno
- Pokreće backend na `http://localhost:8000`
- Pokreće frontend na `http://localhost:5173`

#### Opcija 2: Ručno

**1. Backend Setup**

```bash
# Aktiviraj virtualno okruženje
source venv/bin/activate

# Instaliraj pakete (samo prvi put)
cd backend
pip install -r requirements.txt

# Proveri da li .env postoji i ima sve vrednosti
# Proveri da li service-account-key.json postoji

# Pokreni backend server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend će biti dostupan na `http://localhost:8000`
- API dokumentacija: `http://localhost:8000/docs`

**2. Frontend Setup** (u novom terminalu)

```bash
cd frontend

# Instaliraj pakete (samo prvi put)
npm install

# Proveri da li .env.local postoji (za lokalno razvijanje)
# Ako ne postoji, kopiraj .env.example ili kreiraj .env.local sa:
# VITE_API_URL=http://localhost:8000
# VITE_GOOGLE_CLIENT_ID=your-client-id

# Pokreni frontend server
npm run dev
```

Frontend će biti dostupan na `http://localhost:5173`

### Napomena za Lokalno Razvijanje

- **Frontend**: Koristi `frontend/.env.local` za lokalno razvijanje (već kreiran)
  - `VITE_API_URL=http://localhost:8000` - lokalni backend
- **Produkcija**: Koristi `frontend/.env` za produkciju
  - `VITE_API_URL=https://spc-kpob.onrender.com` - produkcijski backend

## Environment Variables

### Backend (.env)

**Za lokalno razvijanje:**
```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback
JWT_SECRET_KEY=your-secret-key
GOOGLE_SHEETS_CREDENTIALS_PATH=service-account-key.json
GOOGLE_SHEETS_ID=your-sheets-id
GOOGLE_ADMIN_EMAIL=secretary@best.rs
GOOGLE_GROUP_EMAIL=opsta@best.rs
FRONTEND_URL=http://localhost:5173
REDIS_URL=redis://localhost:6379/0  # Opciono
```

**Za produkciju (Render):**
- `GOOGLE_SHEETS_CREDENTIALS` - Service Account JSON kao string (umesto `GOOGLE_SHEETS_CREDENTIALS_PATH`)
- Ostale varijable su iste

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id
```

## Google Cloud Setup

### 1. OAuth Consent Screen

1. Idi na [Google Cloud Console](https://console.cloud.google.com/)
2. Selektuj projekat
3. APIs & Services > OAuth consent screen
4. User Type: **External**
5. Dodaj scopes: `openid`, `email`, `profile`
6. Dodaj Authorized redirect URIs:
   - `http://localhost:5173/auth/callback` (development)
   - `https://your-domain.vercel.app/auth/callback` (production)

### 2. Service Account Setup

1. APIs & Services > Credentials > Create Credentials > Service Account
2. Kreiraj service account i download JSON key
3. Sačuvaj kao `backend/service-account-key.json`
4. Daj pristup Google Sheet-u service account email-u

### 3. Domain-Wide Delegation (za Google Groups)

1. U Service Account postavkama, omogući Domain-Wide Delegation
2. Zabeleži Client ID
3. Idi na [Google Workspace Admin Console](https://admin.google.com/ac/owl/domainwidedelegation)
4. Dodaj novi Client ID sa scope: `https://www.googleapis.com/auth/admin.directory.group.readonly`
5. Omogući Admin SDK API u Google Cloud Console

## Deployment

### Backend (Render)

1. Push kod na GitHub
2. Konektuj GitHub repo sa Render
3. Postavi environment variables:
   - `GOOGLE_CLIENT_ID` - OAuth Client ID
   - `GOOGLE_CLIENT_SECRET` - OAuth Client Secret
   - `JWT_SECRET_KEY` - Generiše se automatski ili postavi svoj
   - `GOOGLE_SHEETS_CREDENTIALS` - **VAŽNO**: Service Account JSON kao string
   - `GOOGLE_SHEETS_ID` - Google Sheets ID
   - `GOOGLE_ADMIN_EMAIL` - `secretary@best.rs`
   - `GOOGLE_GROUP_EMAIL` - `opsta@best.rs`
   - `FRONTEND_URL` - Frontend URL (npr. `https://your-app.vercel.app`)
   - `REDIS_URL` - Opciono, ako koristiš Redis

**Konverzija Service Account JSON u string:**

```bash
# Opcija 1: Koristi skriptu (preporučeno)
cd backend
python3 convert_credentials.py service-account-key.json

# Opcija 2: Koristi Python direktno
python3 -c "import json; print(json.dumps(json.load(open('backend/service-account-key.json'))))"

# Opcija 3: Koristi jq (ako je instaliran)
cat backend/service-account-key.json | jq -c
```

Kopiraj rezultat i postavi kao `GOOGLE_SHEETS_CREDENTIALS` environment variable na Render-u.

**⚠️ VAŽNO**: Na Render-u, `GOOGLE_SHEETS_CREDENTIALS` mora biti postavljen kao environment variable, NE kao fajl. Aplikacija će automatski koristiti environment variable ako postoji, inače će pokušati da učita fajl (samo za lokalno razvijanje).

### Frontend (Vercel)

1. Push kod na GitHub
2. Konektuj GitHub repo sa Vercel
3. Postavi environment variables
4. Deploy

## Features

- Google OAuth autentifikacija
- Role-based access control:
  - Write access: Specifični email-ovi (`hr@best.rs`, `secretary@best.rs`, itd.)
  - View access: Svi `@best.rs` email-ovi + članovi `opsta@best.rs` grupe
- Upis bodova u Google Sheets
- Pregled bodova pojedinačnih članova
- Kandidati za mladog/punopravnog člana
- Fuzzy search za pretragu članova
- Responzivan dizajn

## API Endpoints

- `GET /api/v1/auth/google` - Get Google OAuth URL
- `POST /api/v1/auth/google/callback` - OAuth callback
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/permissions` - Get user permissions
- `POST /api/v1/points/write` - Write points (write access required)
- `GET /api/v1/points/{name}` - Get points for person (view access required)
- `GET /api/v1/points/all` - Get all people (view access required)
- `GET /api/v1/points/candidates/young-member` - Young member candidates (write access required)
- `GET /api/v1/points/candidates/full-member` - Full member candidates (write access required)

API dokumentacija: `http://localhost:8000/docs`

## Tech Stack

**Backend:**
- FastAPI
- Google Sheets API
- Google Admin SDK (Groups)
- JWT authentication
- Redis (opciono)

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- TanStack Query
- React Router

## Troubleshooting

### Backend ne startuje
- Proveri da li su svi paketi instalirani: `pip install -r requirements.txt`
- Proveri da li `.env` fajl postoji i ima sve vrednosti
- Proveri da li `service-account-key.json` postoji

### OAuth ne radi
- Proveri da li je OAuth Consent Screen na "External"
- Proveri da li su redirect URIs tačno dodati
- Sačekaj 5-10 minuta za propagation

### Domain-Wide Delegation greška
- Proveri da li je Service Account Client ID dodat u Google Workspace Admin Console
- Proveri da li je OAuth scope tačno: `https://www.googleapis.com/auth/admin.directory.group.readonly`
- Proveri da li je `GOOGLE_ADMIN_EMAIL` super admin email

### CORS greške
- Proveri da li je `FRONTEND_URL` tačno postavljen u backend `.env`
- Proveri da li je `BACKEND_CORS_ORIGINS` sadrži frontend URL
