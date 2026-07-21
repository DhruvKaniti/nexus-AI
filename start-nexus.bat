@echo off
echo ========================================
echo Starting Nexus Application
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Installing backend dependencies...
cd apps\backend
pip install -r requirements.txt -q
cd ..\..

echo.
echo [2/3] Starting backend server on port 8000...
cd apps\backend
start "Nexus Backend" cmd /k "python -m app.main"
cd ..\..

echo.
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting frontend dev server on port 5173...
cd apps\frontend
start "Nexus Frontend" cmd /k "npm run dev"
cd ..\..

echo.
echo ========================================
echo Nexus is starting!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:5173
echo.
echo Close this window or press Ctrl+C to stop all services
echo.
pause