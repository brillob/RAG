@echo off
REM Setup script for Ollama on Windows
echo ========================================
echo Ollama Setup for RAG System
echo ========================================
echo.

echo Step 1: Checking if Ollama is installed...
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ollama is not installed!
    echo.
    echo Please install Ollama from: https://ollama.com/download
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo [OK] Ollama is installed!
echo.

echo Step 2: Starting Ollama service...
ollama serve >nul 2>&1 &
timeout /t 3 /nobreak >nul
echo [OK] Ollama service started (or already running)
echo.

echo Step 3: Pulling recommended small model (tinyllama)...
echo This is a very small model (~637MB) perfect for RAG tasks on laptops.
echo This may take a few minutes on first run...
ollama pull tinyllama
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to pull model. You can try manually: ollama pull tinyllama
    echo Or try even smaller: ollama pull qwen2.5:0.5b
) else (
    echo [OK] Model downloaded successfully!
)
echo.

echo Step 4: Verifying setup...
ollama list
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your RAG system is now ready to use local LLM.
echo.
echo To test, start the server:
echo   conda activate rag-student-support
echo   python -m app.main
echo.
echo Then visit: http://localhost:8000/docs
echo.
pause
