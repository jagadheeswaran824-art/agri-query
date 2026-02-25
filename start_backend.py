#!/usr/bin/env python3
"""
KrishiSahay Backend Startup Script
Simple script to start the Flask backend server
"""

import os
import sys
import subprocess
import time

def check_python():
    """Check if Python is available"""
    try:
        import sys
        print(f"✅ Python {sys.version} found")
        return True
    except:
        print("❌ Python not found")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "backend_requirements.txt"
        ])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False
    except FileNotFoundError:
        print("❌ pip not found. Please install pip first.")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting KrishiSahay Backend Server...")
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'flask_backend.py'
        os.environ['FLASK_ENV'] = 'development'
        
        # Start the server
        subprocess.run([sys.executable, "flask_backend.py"])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🌾 KrishiSahay Backend Startup                     ║
║                                                       ║
║   Starting Flask server with WebSocket support...    ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("⚠️  Continuing without installing packages...")
        print("   You may need to install them manually:")
        print("   pip install -r backend_requirements.txt")
        time.sleep(2)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()