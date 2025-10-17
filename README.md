# LLM Chatbot - Streamlit + FastAPI

A modern, production-ready chatbot application built with **Streamlit** for the frontend and **FastAPI** for the backend API, powered by OpenAI's GPT models.

## 🚀 Features

- **Modern Architecture**: Clean separation between frontend (Streamlit) and backend (FastAPI)
- **LLM Integration**: Seamless integration with OpenAI GPT models
- **Real-time Chat**: Interactive chat interface with conversation management
- **Configurable**: Extensive configuration options for model parameters
- **Health Monitoring**: Built-in health checks and system monitoring
- **Extensible**: Modular design for easy feature additions
- **Production Ready**: Comprehensive logging, error handling, and validation

## 📁 Project Structure

```
Chatbot/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # This file
│
├── app/                        # Main application package
│   ├── __init__.py
│   ├── api/                    # FastAPI routes and endpoints
│   │   ├── __init__.py
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── api.py          # API router aggregation
│   │       └── endpoints/      # Individual endpoint modules
│   │           ├── __init__.py
│   │           ├── chat.py     # Chat endpoints
│   │           └── health.py   # Health check endpoints
│   │
│   ├── frontend/               # Streamlit frontend
│   │   ├── __init__.py
│   │   ├── streamlit_app.py    # Main Streamlit application
│   │   ├── components/         # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── chat_interface.py
│   │   │   └── sidebar.py
│   │   └── pages/              # Additional pages
│   │       └── __init__.py
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   └── chat_models.py      # Chat-related data models
│   │
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── chat_service.py     # Chat management service
│   │   ├── health_service.py   # Health monitoring service
│   │   └── llm_service.py      # LLM integration service
│   │
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── helpers.py          # General helper functions
│       └── validators.py       # Input validation utilities
│
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── settings.py             # Application settings
│   └── logging_config.py       # Logging configuration
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
│
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
└── logs/                       # Application logs (created at runtime)
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
# Add your OpenAI API key and other configurations
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Secret key for security (change from default)

### 3. Run the Application

#### Option A: Run Both Services Separately

**Terminal 1 - FastAPI Backend:**
```bash
python main.py
```
Backend will be available at: http://localhost:8000

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run app/frontend/streamlit_app.py
```
Frontend will be available at: http://localhost:8501

#### Option B: Using Scripts (if available)
```bash
# Start both services
python scripts/start_services.py
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=4000

# API Configuration
HOST=0.0.0.0
PORT=8000

# Streamlit Configuration
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost

# Security
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/chatbot.log
```

### Model Parameters

Adjustable through the Streamlit interface:
- **Temperature** (0-2): Controls response creativity
- **Max Tokens** (1-4000): Maximum response length
- **Model Selection**: Choose between available GPT models

## 🔌 API Endpoints

### Health Endpoints
- `GET /health` - Basic health check
- `GET /api/v1/health/` - Comprehensive health status
- `GET /api/v1/health/readiness` - Readiness probe

### Chat Endpoints
- `POST /api/v1/chat/message` - Send chat message
- `GET /api/v1/chat/history/{conversation_id}` - Get conversation history
- `POST /api/v1/chat/conversation` - Create new conversation
- `DELETE /api/v1/chat/conversation/{conversation_id}` - Delete conversation

### API Documentation
- Interactive docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 💬 Usage

### Basic Chat Flow

1. **Start the Application**: Run both FastAPI and Streamlit services
2. **Open Frontend**: Navigate to http://localhost:8501
3. **Configure Settings**: Adjust model parameters in the sidebar
4. **Start Chatting**: Type your message and press Send
5. **Manage Conversations**: Create new conversations, export history

### Features

- **Real-time Chat**: Instant responses from AI
- **Conversation Management**: Multiple conversation support
- **Export Functionality**: Download chat history
- **Model Customization**: Adjust AI behavior parameters
- **Health Monitoring**: System status monitoring

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run all tests with coverage
python -m pytest tests/ --cov=app/
```

## 📊 Monitoring & Logging

### Logs
- Application logs: `logs/chatbot.log`
- Structured logging with rotation
- Configurable log levels

### Health Monitoring
- Health endpoints for monitoring
- API connectivity checks
- System resource monitoring

## 🔒 Security Considerations

- Input validation and sanitization
- Rate limiting capabilities
- Secure API key management
- CORS configuration
- SQL injection prevention

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "scripts/start_services.py"]
```

### Production Considerations

- Use environment-specific settings
- Configure proper logging levels
- Set up reverse proxy (nginx)
- Implement proper monitoring
- Use database for conversation storage
- Configure SSL/TLS

## 🛠️ Development

### Adding New Features

1. **API Endpoints**: Add to `app/api/v1/endpoints/`
2. **Services**: Add business logic to `app/services/`
3. **Models**: Define data models in `app/models/`
4. **Frontend Components**: Add UI components to `app/frontend/components/`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Implement proper error handling

## 📚 Dependencies

### Core Dependencies
- **FastAPI**: Web framework for APIs
- **Streamlit**: Frontend framework
- **OpenAI**: LLM integration
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ❓ Troubleshooting

### Common Issues

**OpenAI API Errors:**
- Verify API key is correct
- Check API quota and billing
- Ensure model is available

**Connection Issues:**
- Check network connectivity
- Verify ports are not blocked
- Ensure services are running

**Performance Issues:**
- Reduce max_tokens for faster responses
- Check system resources
- Consider upgrading OpenAI plan

### Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Create an issue in the repository

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - Streamlit + FastAPI architecture
  - OpenAI GPT integration
  - Basic chat functionality
  - Health monitoring
  - Comprehensive documentation