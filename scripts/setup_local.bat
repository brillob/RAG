@echo off
REM Setup script for local testing (Windows)

echo 🚀 Setting up RAG Student Support for local testing...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.local.example .env >nul
    echo ✓ Created .env file. You can edit it if needed.
) else (
    echo ✓ .env file already exists
)

echo.
echo ✅ Setup complete!
echo.
echo To run the server:
echo   venv\Scripts\activate
echo   python -m app.main
echo.
echo To test:
echo   python scripts\test_local.py --query "What are the admission requirements?"
echo.

pause
