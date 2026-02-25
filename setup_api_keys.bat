@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                               ║
echo ║   🔑 KrishiSahay API Key Configuration                                       ║
echo ║   IBM Watsonx Granite LLM Setup                                              ║
echo ║                                                                               ║
echo ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the setup script
python setup_api_keys.py

echo.
pause