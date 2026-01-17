@echo off
REM Setup script for Anaconda/Conda environment (Windows)

echo 🚀 Setting up RAG Student Support with Conda...

REM Check if conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda is not installed or not in PATH
    echo    Please install Anaconda or Miniconda
    echo    Or use Anaconda Prompt instead of regular Command Prompt
    pause
    exit /b 1
)

echo ✓ Conda found

REM Check if environment.yml exists
if not exist "environment.yml" (
    echo ❌ environment.yml not found
    echo    Creating from requirements.txt...
    echo    Please run this script again after environment.yml is created
    pause
    exit /b 1
)

REM Check if environment already exists
conda env list | findstr "rag-student-support" >nul 2>&1
if not errorlevel 1 (
    echo ⚠ Conda environment 'rag-student-support' already exists
    echo    Updating environment...
    conda env update -f environment.yml --prune
) else (
    echo 📦 Creating conda environment from environment.yml...
    conda env create -f environment.yml
)

if errorlevel 1 (
    echo ❌ Failed to create/update conda environment
    pause
    exit /b 1
)

echo.
echo ✅ Conda environment setup complete!
echo.
echo To activate the environment:
echo   conda activate rag-student-support
echo.
echo Then you can:
echo   - Run the server: python -m app.main
echo   - Process handbook: python scripts/process_handbook.py
echo   - Run tests: pytest
echo.
echo To deactivate: conda deactivate
echo.

pause
