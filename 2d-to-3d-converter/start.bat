@echo off
REM 2D to 3D Converter - Startup Script for Windows
REM This script starts the Flask backend server

echo ==========================================
echo 2D to 3D Model Converter
echo Starting Backend Server...
echo ==========================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "backend\requirements.txt" (
    echo Error: requirements.txt not found!
    pause
    exit /b 1
)

echo Checking dependencies...
pip install -q -r backend\requirements.txt

REM Start Flask server
echo Starting Flask server...
echo.
cd backend
python app.py

pause
