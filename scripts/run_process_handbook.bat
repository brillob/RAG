@echo off
REM Batch script to run process_handbook.py with proper environment setup

echo Checking conda environment...

REM Check if conda is available
where conda >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda is not in PATH
    echo Please activate your conda environment first:
    echo   conda activate rag-student-support
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
echo.

REM Change to project directory
cd /d "%~dp0.."

REM Run the script
echo Running process_handbook.py...
python scripts\process_handbook.py %*

pause
