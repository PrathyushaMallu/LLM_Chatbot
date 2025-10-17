@echo off
echo 🤖 LLM Chatbot Services Launcher
echo ================================
echo.
echo This will start the chatbot services with options for:
echo • FastAPI Backend (API Server)
echo • Streamlit Frontend (Web UI)  
echo • Both Services Together
echo.
echo 🔹 All Available API Endpoints:
echo    • Health Check: GET /api/v1/health
echo    • Chat Messages: POST /api/v1/chat/message
echo    • Chat History: GET /api/v1/chat/history/{user_id}
echo    • User Registration: POST /api/v1/auth/register
echo    • User Login: POST /api/v1/auth/login
echo    • User Profile: GET /api/v1/users/profile
echo    • Update Profile: PUT /api/v1/users/profile
echo    • Admin System Status: GET /api/v1/admin/system/status
echo    • Admin Analytics: GET /api/v1/admin/analytics
echo    • Gemini Providers: GET /api/v1/gemini/providers
echo    • Gemini Registration: POST /api/v1/gemini/register
echo    • Gemini Test: POST /api/v1/gemini/test
echo.
echo 🌐 Frontend Application URLs:
echo    • API Documentation: http://localhost:8001/docs
echo    • Interactive ReDoc: http://localhost:8001/redoc
echo    • Streamlit Chat UI: http://localhost:8501
echo.
echo ================================================
echo.

cd /d "%~dp0"
python start_services.py

echo.
echo 👋 Chatbot services launcher finished!
pause