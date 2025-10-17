"""
Startup script to launch both FastAPI and Streamlit services.
"""

import subprocess
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_fastapi():
    """Start the FastAPI server."""
    try:
        logger.info("Starting FastAPI server...")
        return subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except Exception as e:
        logger.error(f"Failed to start FastAPI: {e}")
        return None


def start_streamlit():
    """Start the Streamlit app."""
    try:
        logger.info("Starting Streamlit app...")
        return subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "app/frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except Exception as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return None


def main():
    """Main function to start both services."""
    logger.info("🚀 Starting LLM Chatbot Services...")
    
    # Check if we're in the correct directory
    if not Path("main.py").exists():
        logger.error("Please run this script from the project root directory")
        sys.exit(1)
    
    # Start FastAPI
    fastapi_process = start_fastapi()
    if not fastapi_process:
        logger.error("Failed to start FastAPI server")
        sys.exit(1)
    
    # Wait a moment for FastAPI to start
    time.sleep(3)
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    if not streamlit_process:
        logger.error("Failed to start Streamlit app")
        fastapi_process.terminate()
        sys.exit(1)
    
    logger.info("✅ Both services started successfully!")
    logger.info("📊 FastAPI: http://localhost:8000")
    logger.info("🎨 Streamlit: http://localhost:8501")
    logger.info("📚 API Docs: http://localhost:8000/api/v1/docs")
    logger.info("\nPress Ctrl+C to stop both services")
    
    try:
        # Wait for both processes
        fastapi_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping services...")
        fastapi_process.terminate()
        streamlit_process.terminate()
        
        # Wait for processes to terminate
        fastapi_process.wait(timeout=5)
        streamlit_process.wait(timeout=5)
        
        logger.info("✅ Services stopped successfully")


if __name__ == "__main__":
    main()