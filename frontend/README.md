# SPC Frontend

React + TypeScript frontend za Sistem Praćenja Članstva web aplikaciju.

## Setup

1. Instaliraj dependencies:
```bash
npm install
```

2. Kopiraj `.env.example` u `.env` i popuni vrednosti:
```bash
cp .env.example .env
```

3. Pokreni development server:
```bash
npm run dev
```

Aplikacija će biti dostupna na `http://localhost:5173`

## Build za Production

```bash
npm run build
```

Build fajlovi će biti u `dist/` folderu.

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_GOOGLE_CLIENT_ID` - Google OAuth Client ID

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- TanStack Query (React Query)
- React Router
- Axios
