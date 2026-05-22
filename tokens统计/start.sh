#!/bin/bash
echo "========================================"
echo "  AI Token Tracker - Starting..."
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python not found. Please install Python first."
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found. Please install Node.js first."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install backend dependencies
echo "[1/4] Installing backend dependencies..."
cd "$SCRIPT_DIR/backend"
$PYTHON -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt -q

# Install frontend dependencies
echo "[2/4] Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
[ ! -d "node_modules" ] && npm install

# Start backend
echo "[3/4] Starting backend server..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate 2>/dev/null || true
$PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "[4/4] Starting frontend server..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
