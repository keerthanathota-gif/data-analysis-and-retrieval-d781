@echo off
REM Windows batch script to check database contents

echo ================================================================
echo CPSC REGULATION SYSTEM - DATABASE CHECK (Windows)
echo ================================================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.x and add it to PATH
    pause
    exit /b 1
)

REM Check if database exists
set DB_PATH=backend\cfr_data.db

if exist "%DB_PATH%" (
    echo Found database at: %CD%\%DB_PATH%
    echo.
    python check_database.py "%DB_PATH%"
) else (
    echo ERROR: Database not found at: %CD%\%DB_PATH%
    echo.
    echo Please provide the correct path to your cfr_data.db file
    echo.
    echo Usage:
    echo   python check_database.py "C:\path\to\cfr_data.db"
    echo.
)

echo.
pause
