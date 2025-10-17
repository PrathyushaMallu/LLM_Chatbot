"""
Simple startup script for the chatbot services.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI Backend...")
    cmd = [sys.executable, "-c", "import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8001)"]
    return subprocess.Popen(cmd, cwd=Path.cwd())


def start_frontend():
    """Start the Streamlit frontend."""
    print("🎨 Starting Streamlit Frontend...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app/frontend/streamlit_app.py", "--server.port", "8501"]
    return subprocess.Popen(cmd, cwd=Path.cwd())


def main():
    """Main startup function."""
    print("🤖 Chatbot Services Startup")
    print("=" * 40)
    
    print("\nChoose startup option:")
    print("1. Backend Only (API Server)")
    print("2. Frontend Only (Web UI)")
    print("3. Both Services")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\nStartup cancelled.")
        return
    
    processes = []
    
    if choice == "1":
        processes.append(start_backend())
        print("\n✅ Backend started!")
        print("📍 API Server: http://localhost:8001")
        print("📖 API Docs: http://localhost:8001/docs")
        
    elif choice == "2":
        processes.append(start_frontend())
        print("\n✅ Frontend started!")
        print("📍 Web UI: http://localhost:8501")
        
    elif choice == "3":
        processes.append(start_backend())
        time.sleep(3)  # Wait for backend to start
        processes.append(start_frontend())
        
        print("\n✅ Both services started!")
        print("📍 Backend API: http://localhost:8001")
        print("📍 Frontend UI: http://localhost:8501")
        print("📖 API Docs: http://localhost:8001/docs")
        
        # Open browser tabs
        time.sleep(2)
        webbrowser.open("http://localhost:8001/docs")
        time.sleep(1)
        webbrowser.open("http://localhost:8501")
        
    else:
        print("Invalid choice. Exiting.")
        return
    
    if processes:
        print(f"\n💡 Press Ctrl+C to stop all services")
        try:
            # Wait for processes
            for process in processes:
                process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping services...")
            for process in processes:
                process.terminate()
            print("👋 All services stopped!")


if __name__ == "__main__":
    main()