@echo off
echo ========================================
echo  Badminton Analysis Platform - Startup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

echo [1/4] Setting up Python virtual environment...
cd backend
if not exist "venv" (
    python -m venv venv
)

echo [2/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet

echo [3/4] Installing frontend dependencies...
cd ..\frontend
if not exist "node_modules" (
    call npm install
)

echo [4/4] Starting servers...
echo.
echo Starting Backend Server on http://localhost:8000
echo Starting Frontend Server on http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

:: Start backend in background
start "Backend Server" cmd /c "cd ..\backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
call npm run dev
