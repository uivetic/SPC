#!/bin/bash

# SPC Web App - Start Script
# Pokreće backend i frontend aplikaciju

echo "🚀 Pokretanje SPC aplikacije..."
echo ""

# Proveri da li postoji venv
if [ ! -d "venv" ]; then
    echo "❌ Virtualno okruženje ne postoji. Kreiranje..."
    python3 -m venv venv
fi

# Aktiviraj venv
echo "📦 Aktiviranje virtualnog okruženja..."
source venv/bin/activate

# Proveri da li su paketi instalirani
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📥 Instalacija backend paketa..."
    cd backend
    pip install -r requirements.txt
    cd ..
fi

# Proveri da li su frontend paketi instalirani
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 Instalacija frontend paketa..."
    cd frontend
    npm install
    cd ..
fi

# Proveri .env fajlove
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env ne postoji! Kopiraj backend/.env.example i popuni vrednosti."
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    echo "⚠️  frontend/.env ne postoji! Kopiraj frontend/.env.example i popuni vrednosti."
    exit 1
fi

# Proveri da li je service-account-key.json prisutan
if [ ! -f "backend/service-account-key.json" ]; then
    echo "⚠️  backend/service-account-key.json ne postoji!"
    echo "   Dodaj Google Service Account JSON fajl u backend/ folder."
    exit 1
fi

echo ""
echo "✅ Sve je spremno!"
echo ""
echo "🌐 Pokretanje backend servera na http://localhost:8000"
echo "🎨 Pokretanje frontend servera na http://localhost:5173"
echo ""
echo "Pritisni Ctrl+C za zaustavljanje oba servera"
echo ""

# Pokreni backend u pozadini
cd backend
source ../venv/bin/activate
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Sačekaj malo da backend startuje
sleep 2

# Pokreni frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Funkcija za cleanup
cleanup() {
    echo ""
    echo "🛑 Zaustavljanje servera..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Čekaj da se procesi završe
wait

