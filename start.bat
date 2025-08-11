@echo off
REM 4Real Music Application Startup Script for Windows
REM This script starts the nonix_mini_artist application

echo 🎵 Starting 4Real Music Application...
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  No virtual environment found. Using system Python...
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Required dependencies not found
    echo Please install requirements: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start the application
echo 🚀 Launching application...
echo.

REM Try to start from main.py first, then from the src directory
if exist "main.py" (
    echo Starting from main.py...
    python main.py
) else if exist "src\nonix_mini_artist\ui\app.py" (
    echo Starting from UI app...
    cd src\nonix_mini_artist\ui
    python app.py
    cd ..\..\..
) else (
    echo ❌ Error: Could not find main entry point
    echo Available files:
    dir *.py 2>nul || echo No Python files in root
    if exist "src" dir src\nonix_mini_artist\ui\*.py 2>nul || echo No UI files found
    pause
    exit /b 1
)

echo.
echo 👋 Application closed
pause
