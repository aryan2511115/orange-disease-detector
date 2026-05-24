@echo off
REM Orange Disease Detection System - Windows Startup Script

echo.
echo ========================================================================
echo  ORANGE DISEASE DETECTION SYSTEM - STARTUP
echo ========================================================================
echo.

REM Get the project root directory
set PROJECT_ROOT=%CD%

echo Project Root: %PROJECT_ROOT%
echo.

REM Step 1: Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo OK %PYTHON_VERSION%
echo.

REM Step 2: Create virtual environment
echo Setting up virtual environment...
if not exist venv (
    echo Creating venv directory...
    python -m venv venv
    echo OK Virtual environment created
) else (
    echo OK Virtual environment already exists
)
echo.

REM Step 3: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo OK Virtual environment activated
echo.

REM Step 4: Install requirements
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed properly
)
echo.

REM Step 5: Create necessary directories
echo Creating necessary directories...
if not exist dataset\preprocessed mkdir dataset\preprocessed
if not exist models mkdir models
if not exist static\uploads mkdir static\uploads
if not exist logs mkdir logs
echo OK Directories created
echo.

REM Step 6: Start the application
echo ========================================================================
echo  STARTING APPLICATION
echo ========================================================================
echo.
echo   Web Interface: http://localhost:5000/
echo   API Endpoint:  http://localhost:5000/api/
echo   Health Check:  http://localhost:5000/api/health
echo.
echo   Press Ctrl+C to stop the server
echo.
echo ========================================================================
echo.

cd backend
python app.py

pause
