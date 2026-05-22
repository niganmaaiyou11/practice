@echo off
echo ========================================
echo   AI Token Tracker - Starting...
echo ========================================

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

:: Install backend dependencies if needed
echo [1/4] Checking backend dependencies...
cd /d "%~dp0backend"
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

:: Install frontend dependencies if needed
echo [2/4] Checking frontend dependencies...
cd /d "%~dp0frontend"
if not exist "node_modules\" (
    echo Installing frontend packages...
    call npm install
)

:: Start backend
echo [3/4] Starting backend server...
cd /d "%~dp0backend"
start "Token Tracker Backend" cmd /c "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Start frontend
echo [4/4] Starting frontend server...
cd /d "%~dp0frontend"
start "Token Tracker Frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Close this window after you're done.
pause
