@echo off
echo.
echo ╔═══════════════════════════════════════════════════════╗
echo ║                                                       ║
echo ║   🌾 KrishiSahay Backend Server                      ║
echo ║                                                       ║
echo ║   Starting Flask server with WebSocket support...    ║
echo ║                                                       ║
echo ╚═══════════════════════════════════════════════════════╝
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

REM Install requirements
echo 📦 Installing required packages...
python -m pip install -r backend_requirements.txt
if errorlevel 1 (
    echo ⚠️  Some packages may not have installed correctly
    echo    Continuing anyway...
)

echo.
echo 🚀 Starting KrishiSahay Backend Server...
echo.
echo    Server will be available at: http://localhost:5000
echo    Press Ctrl+C to stop the server
echo.

REM Start the Flask server
python flask_backend.py

echo.
echo 🛑 Server stopped
pause