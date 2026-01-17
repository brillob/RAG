@echo off
REM Script to install all dependencies in the conda environment

echo ========================================
echo Installing RAG Dependencies
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda is not in PATH
    echo Please use Anaconda Prompt or add conda to PATH
    pause
    exit /b 1
)

REM Check if we're in a conda environment
if "%CONDA_DEFAULT_ENV%"=="" (
    echo WARNING: No conda environment is active
    echo Attempting to activate rag-student-support...
    call conda activate rag-student-support
    if errorlevel 1 (
        echo ERROR: Could not activate rag-student-support
        echo Please activate manually: conda activate rag-student-support
        pause
        exit /b 1
    )
)

echo Using conda environment: %CONDA_DEFAULT_ENV%
echo Python path:
python -c "import sys; print(sys.executable)"
echo.

REM Change to project directory
cd /d "%~dp0.."

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
echo.

echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
echo.

echo Verifying installation...
python scripts/verify_dependencies.py
echo.

echo ========================================
echo Installation complete!
echo ========================================
pause
