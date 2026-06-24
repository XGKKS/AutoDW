@echo off
setlocal enabledelayedexpansion

set "BASE_DIR=%~dp0"

echo ================================================
echo   Data Warehouse AI Assistant - Startup Script
echo ================================================
echo.

echo [1/4] Checking port status...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Port 8000 is in use, killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Port 5173 is in use, killing PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo [2/4] Starting backend service...
start "Backend Server" cmd /k "cd /d ""%BASE_DIR%backend"" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"

timeout /t 3 /nobreak >nul

echo [3/4] Starting frontend service...
start "Frontend Server" cmd /k "cd /d ""%BASE_DIR%frontend"" && npm run dev"

timeout /t 5 /nobreak >nul

echo [4/4] Opening browser...
start http://localhost:5173

echo.
echo ================================================
echo   Services started successfully!
echo   Frontend: http://localhost:5173
echo   Backend: http://localhost:8000
echo ================================================
pause
