#!/usr/bin/env python3
"""
Startup script for the Mindmap Generator System
Handles environment setup and server launch
"""

import os
import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if required files exist"""
    required_files = [
        "mindmap_generator.py",
        "server.py",
        "requirements.txt"
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n📋 Please make sure all files are in the same directory:")
        print("   - mindmap_generator.py (your main script)")
        print("   - server.py (the FastAPI backend)")
        print("   - requirements.txt (dependencies)")
        print("   - run_server.py (this file)")
        return False

    return True

def check_api_key():
    """Check if Anthropic API key is set"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY environment variable not found!")
        print("\n🔑 To set your API key:")
        print("   Windows: set ANTHROPIC_API_KEY=your_api_key_here")
        print("   Mac/Linux: export ANTHROPIC_API_KEY=your_api_key_here")
        print("\n💡 Or create a .env file with:")
        print("   ANTHROPIC_API_KEY=your_api_key_here")

        # Ask if they want to continue anyway
        response = input("\n❓ Continue without API key? (y/n): ").lower()
        if response != 'y':
            return False
    else:
        print(f"✅ API key found: {api_key[:8]}...{api_key[-4:]}")

    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Mindmap Generator Server...")
    print("🌐 Web interface will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)

    try:
        # Import and run the server
        import uvicorn
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Please run: pip install -r requirements.txt")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def main():
    """Main startup function"""
    print("🧠 Mindmap Generator System Startup")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check API key
    if not check_api_key():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()