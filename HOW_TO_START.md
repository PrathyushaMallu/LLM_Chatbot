# 🤖 Chatbot Startup Guide

## Quick Start Options

### Option 1: Double-click to Start (Easiest)
1. Navigate to your project folder: `c:\Prathyu_Amzur\vsCodeProjects\Chatbot`
2. Double-click `start_chatbot.bat`
3. The chatbot will start automatically on http://localhost:8001

### Option 2: Command Line
```bash
cd "c:\Prathyu_Amzur\vsCodeProjects\Chatbot"
python main.py
```

### Option 3: Custom Port
```bash
cd "c:\Prathyu_Amzur\vsCodeProjects\Chatbot"
python -c "import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8002)"
```

---

## 🌐 Access Your Chatbot

Once started, your chatbot is available at:

| Service | URL | Description |
|---------|-----|-------------|
| **API Server** | http://localhost:8001 | Main API endpoint |
| **Interactive Docs** | http://localhost:8001/api/v1/docs | Swagger UI for testing |
| **Alternative Docs** | http://localhost:8001/api/v1/redoc | ReDoc documentation |
| **Health Check** | http://localhost:8001/api/v1/health | Server status |

---

## 🚀 Quick Test Commands

### 1. Test Server Health
```bash
curl http://localhost:8001/api/v1/health
```

### 2. Chat with Gemini AI
```bash
curl -X POST "http://localhost:8001/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! How are you today?",
    "user_id": "test_user",
    "provider": "gemini",
    "model": "gemini-2.5-flash"
  }'
```

### 3. Check Available Providers
```bash
curl http://localhost:8001/api/v1/gemini/providers
```

---

## 🎯 Key Features Available

### ✅ **AI Chat with Gemini**
- Use Google's latest Gemini 2.5 Flash model
- Fast response times (< 1 second)
- Multi-turn conversations
- Custom temperature and token limits

### ✅ **Multi-Provider Support**
- Google Gemini (configured)
- OpenAI GPT (can be added)
- Provider switching per message

### ✅ **Complete API**
- RESTful endpoints
- Authentication & authorization
- User management
- Admin panel
- Rate limiting
- Health monitoring

### ✅ **Interactive Documentation**
- Swagger UI at `/docs`
- Test endpoints directly in browser
- Auto-generated API specs

---

## 🔧 Troubleshooting

### Port Already in Use
If you get a port error, try:
```bash
python -c "import uvicorn; from main import app; uvicorn.run(app, host='localhost', port=8002)"
```

### Python Path Issues
Make sure you're in the project directory:
```bash
cd "c:\Prathyu_Amzur\vsCodeProjects\Chatbot"
```

### Missing Dependencies
Install requirements:
```bash
pip install -r requirements.txt
```

---

## 📱 Usage Examples

### Web Browser
1. Go to http://localhost:8001/docs
2. Try the `/api/v1/chat/message` endpoint
3. Fill in the request body:
```json
{
  "message": "Tell me a joke",
  "user_id": "demo_user",
  "provider": "gemini"
}
```

### Python Script
```python
import requests

response = requests.post("http://localhost:8001/api/v1/chat/message", json={
    "message": "What's the weather like?",
    "user_id": "python_user",
    "provider": "gemini",
    "model": "gemini-2.5-flash"
})

print(response.json()["message"])
```

### JavaScript/Fetch
```javascript
fetch('http://localhost:8001/api/v1/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Hello from JavaScript!",
    user_id: "js_user",
    provider: "gemini"
  })
})
.then(response => response.json())
.then(data => console.log(data.message));
```

---

## 🛑 How to Stop

- **Command Line**: Press `Ctrl+C`
- **Batch File**: Close the window or press `Ctrl+C`
- **Task Manager**: End the Python process if needed

---

## 🎉 You're Ready!

Your chatbot is now fully functional with:
- ✅ Gemini AI integration
- ✅ RESTful API
- ✅ Interactive documentation
- ✅ Authentication system
- ✅ Admin panel
- ✅ Comprehensive testing

**Start chatting and enjoy your AI-powered chatbot!** 🤖✨