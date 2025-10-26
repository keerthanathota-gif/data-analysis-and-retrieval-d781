@echo off
echo ========================================
echo   Restarting Backend Server
echo ========================================

echo.
echo [1] Stopping all Python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo     Killing process %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo [2] Waiting for processes to stop...
timeout /t 3 /nobreak >nul

echo.
echo [3] Starting backend server...
cd "%~dp0"
python run.py

pause
