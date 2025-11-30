# Google OAuth Setup - Detaljna Uputstva

## Problem
Greška "The OAuth client was not found" znači da Google OAuth Client ID nije validan ili ne postoji.

## Rešenje: Kreiranje Google OAuth Credentials

### Korak 1: Google Cloud Console Setup

1. **Idite na Google Cloud Console**
   - Otvorite: https://console.cloud.google.com/
   - Prijavite se sa Google nalogom

2. **Kreirajte novi projekat ili izaberite postojeći**
   - Kliknite na dropdown sa imenom projekta (gore levo)
   - Kliknite "NEW PROJECT"
   - Unesite ime: "SPC Web App"
   - Kliknite "CREATE"

3. **Omogućite Google+ API**
   - U meniju (hamburger), idite na "APIs & Services" > "Library"
   - Pretražite "Google+ API" ili "Google Identity"
   - Kliknite na "Google Identity" ili "Google+ API"
   - Kliknite "ENABLE"

4. **Kreirajte OAuth 2.0 Client ID**
   - Idite na "APIs & Services" > "Credentials"
   - Kliknite "+ CREATE CREDENTIALS" > "OAuth client ID"
   - Ako se pojavi upozorenje o OAuth consent screen:
     - Kliknite "CONFIGURE CONSENT SCREEN"
     - Izaberite "External" (za testiranje)
     - Kliknite "CREATE"
     - Popunite:
       - App name: "SPC Web App"
       - User support email: vaš email
       - Developer contact: vaš email
     - Kliknite "SAVE AND CONTINUE" kroz sve korake
     - Na kraju kliknite "BACK TO DASHBOARD"
   
   - Sada kreirajte OAuth Client ID:
     - Application type: **Web application**
     - Name: "SPC Web App"
     - **Authorized JavaScript origins:**
       - `http://localhost:5173`
     - **Authorized redirect URIs:**
       - `http://localhost:5173/auth/callback`
       - `http://localhost:8000/api/v1/auth/google/callback`
     - Kliknite "CREATE"

5. **Kopirajte Credentials**
   - Nakon kreiranja, videćete popup sa:
     - **Client ID** (dugačak string koji počinje sa brojevima)
     - **Client Secret** (takođe dugačak string)
   - **VAŽNO:** Kopirajte oba odmah - Client Secret se neće moći videti ponovo!

### Korak 2: Ažuriranje .env fajlova

#### Backend `.env` fajl:

```env
# Google OAuth
GOOGLE_CLIENT_ID=VAŠ_CLIENT_ID_OVDE
GOOGLE_CLIENT_SECRET=VAŠ_CLIENT_SECRET_OVDE
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# JWT
JWT_SECRET_KEY=generiši-random-string-ovde
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=../credentials.json
GOOGLE_SHEETS_ID=17yR3BJzslf4HLMGTDc0OvzRaY3t7VAZ1-CGx5GxQM_Q

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://localhost:5173

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### Frontend `.env` fajl:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=ISTI_CLIENT_ID_KAO_U_BACKEND
```

### Korak 3: Generisanje JWT Secret Key

```bash
# U terminalu:
openssl rand -hex 32
```

Kopirajte rezultat i stavite ga u `JWT_SECRET_KEY` u backend `.env` fajlu.

### Korak 4: Restart Servera

Nakon ažuriranja `.env` fajlova, restartujte oba servera:

**Terminal 1 - Backend:**
```bash
# Pritisnite Ctrl+C da zaustavite
# Zatim ponovo pokrenite:
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
# Pritisnite Ctrl+C da zaustavite
# Zatim ponovo pokrenite:
cd frontend
npm run dev
```

### Korak 5: Testiranje

1. Otvorite http://localhost:5173
2. Kliknite "Sign in with Google"
3. Trebalo bi da vidite Google login stranicu
4. Nakon prijave, bićete preusmereni nazad na aplikaciju

## Troubleshooting

### "invalid_client" greška
- Proverite da li je Client ID tačno kopiran (bez razmaka)
- Proverite da li je Client ID isti u oba `.env` fajla
- Proverite da li su redirect URIs tačno dodati u Google Cloud Console

### "redirect_uri_mismatch" greška
- Proverite da li je redirect URI u Google Cloud Console tačno: `http://localhost:5173/auth/callback`
- Proverite da li je `GOOGLE_REDIRECT_URI` u backend `.env` isti

### CORS greške
- Proverite da li je `BACKEND_CORS_ORIGINS` u backend `.env` uključuje `http://localhost:5173`
- Proverite da li je `FRONTEND_URL` postavljen na `http://localhost:5173`

## Napomena

Za production deployment, trebaće vam:
- Verifikovani OAuth consent screen
- Production redirect URIs (npr. `https://yourdomain.com/auth/callback`)
- HTTPS umesto HTTP

