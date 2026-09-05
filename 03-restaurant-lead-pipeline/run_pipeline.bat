@echo off
echo ========================================
echo Restaurant Lead Generation Pipeline
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found! Starting pipeline...
echo.

REM Run the startup script
python start_pipeline.py

echo.
echo Pipeline execution completed.
pause
