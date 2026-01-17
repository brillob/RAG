@echo off
REM Generate HTML viewers for all markdown files
REM This script requires Python with markdown library

echo Generating HTML viewers for markdown files...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python or add it to PATH.
    echo.
    echo Alternatively, you can install markdown library:
    echo   pip install markdown
    echo.
    echo Then run: python scripts/generate_html_viewers.py
    pause
    exit /b 1
)

REM Check if markdown library is installed
python -c "import markdown" >nul 2>&1
if errorlevel 1 (
    echo Installing markdown library...
    pip install markdown
)

REM Run the Python script
python scripts/generate_html_viewers.py

if errorlevel 1 (
    echo.
    echo Error generating HTML files. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo HTML files generated successfully!
echo Open docs_html/index.html in your browser to view all documentation.
pause
