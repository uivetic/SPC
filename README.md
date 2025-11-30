# SPC Web App - Sistem Praćenja Članstva

Modern web aplikacija za praćenje članstva i bodova, migrirana sa PyQt5 desktop aplikacije.

## Struktura Projekta

```
SPC/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # Business logic
│   │   └── main.py   # FastAPI app
│   └── requirements.txt
│
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   └── package.json
│
└── [original files]  # Originalna desktop aplikacija
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Popuni .env fajl
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Popuni .env fajl
npm run dev
```

## Deployment

### Backend (Render/Railway)

1. Push kod na GitHub
2. Konektuj GitHub repo sa Render/Railway
3. Postavi environment variables
4. Deploy

### Frontend (Vercel)

1. Push kod na GitHub
2. Konektuj GitHub repo sa Vercel
3. Postavi environment variables
4. Deploy

## Features

- ✅ Google OAuth autentifikacija
- ✅ Upis bodova u Google Sheets
- ✅ Pregled bodova pojedinačnih članova
- ✅ Fuzzy search za pretragu članova
- ✅ Responzivan dizajn (mobile-friendly)
- ✅ Async operacije (ne blokira UI)
- ✅ Modern UI sa Tailwind CSS

## Tech Stack

**Backend:**
- FastAPI
- Google Sheets API
- JWT authentication
- Redis (opciono za caching)

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- TanStack Query
- React Router
