@echo off
echo 🤖 Starting LLM Chatbot Services...
echo.
echo Choose your startup option:
echo [1] FastAPI Backend Only (API Server)
echo [2] Streamlit Frontend Only (Web UI)
echo [3] Both Services (Full Application)
echo.
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
echo Invalid choice. Starting FastAPI backend by default...
goto backend

:backend
echo.
echo 🚀 Starting FastAPI Backend Server...
echo.
echo 📍 API Server: http://localhost:8001
echo 📖 API Documentation: http://localhost:8001/docs
echo 🔄 Alternative Docs: http://localhost:8001/redoc
echo.
echo 🔹 Available API Endpoints:
echo    • Health Check: GET /api/v1/health
echo    • Chat Messages: POST /api/v1/chat/message
echo    • Chat History: GET /api/v1/chat/history
echo    • User Registration: POST /api/v1/auth/register
echo    • User Login: POST /api/v1/auth/login
echo    • User Profile: GET /api/v1/users/profile
echo    • Admin Status: GET /api/v1/admin/system/status
echo    • Gemini Providers: GET /api/v1/gemini/providers
echo    • Gemini Registration: POST /api/v1/gemini/register
echo.
echo 🎯 Your Gemini API is configured and ready!
echo 💡 Press Ctrl+C to stop the server
echo ================================================
echo.
cd /d "%~dp0"
python -c "import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8001)"
goto end

:frontend
echo.
echo 🎨 Starting Streamlit Frontend...
echo.
echo 📍 Frontend UI: http://localhost:8501
echo 🔧 Make sure FastAPI backend is running on port 8001
echo.
echo 💡 Press Ctrl+C to stop the frontend
echo ================================================
echo.
cd /d "%~dp0"
streamlit run app/frontend/streamlit_app.py --server.port 8501
goto end

:both
echo.
echo 🚀 Starting Both Backend and Frontend Services...
echo.
echo 📍 API Server: http://localhost:8001
echo 📍 Frontend UI: http://localhost:8501
echo 📖 API Documentation: http://localhost:8001/docs
echo.
echo 🔹 Complete Application Stack:
echo    • FastAPI Backend: http://localhost:8001
echo    • Streamlit Frontend: http://localhost:8501
echo    • API Documentation: http://localhost:8001/docs
echo    • Interactive Chat UI: http://localhost:8501
echo.
echo 🎯 Starting FastAPI backend first...
cd /d "%~dp0"
start "FastAPI Backend" cmd /k "python -c \"import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8001)\""
echo 🎯 Waiting for backend to start...
timeout /t 3 /nobreak >nul
echo 🎯 Starting Streamlit frontend...
start "Streamlit Frontend" cmd /k "streamlit run app/frontend/streamlit_app.py --server.port 8501"
echo.
echo ✅ Both services are starting in separate windows!
echo 📍 Backend API: http://localhost:8001
echo � Frontend UI: http://localhost:8501
echo.
echo Press any key to close this window...
pause >nul
goto end

:end
echo.
echo �👋 Chatbot services stopped successfully!
pause