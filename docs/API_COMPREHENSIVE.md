# Chatbot API Documentation

## Overview

This comprehensive REST API provides a complete chatbot service with user management, authentication, conversation handling, and administrative features. Built with FastAPI and featuring OpenAI GPT integration.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API supports multiple authentication methods:

### 1. JWT Bearer Tokens
```bash
Authorization: Bearer <access_token>
```

### 2. API Keys
```bash
Authorization: ApiKey <api_key>
```

### 3. Admin Token (for admin endpoints)
```bash
Authorization: Bearer <admin_secret_key>
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_info": {
    "user_id": "user_12345",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "is_admin": false
  }
}
```

#### POST /auth/login
Authenticate user and get tokens.

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:** Same as registration response.

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1Q..."
}
```

#### POST /auth/logout
Logout and invalidate tokens.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Successfully logged out",
  "user_id": "user_12345",
  "logged_out_at": "2023-10-09T15:30:00Z"
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <access_token>`

#### POST /auth/generate-api-key
Generate a new API key for the user.

**Headers:** `Authorization: Bearer <access_token>`

#### POST /auth/change-password
Change user password.

**Headers:** `Authorization: Bearer <access_token>`

**Form Data:**
- `current_password`: Current password
- `new_password`: New password (min 8 chars)

### Health Endpoints

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-09T15:30:00Z",
  "version": "1.0.0"
}
```

#### GET /health/detailed
Detailed health status including system metrics.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-09T15:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "llm_service": "healthy",
    "memory_usage": 67.5,
    "cpu_usage": 23.1
  },
  "system_info": {
    "python_version": "3.11.0",
    "platform": "Windows-10",
    "uptime_seconds": 3600
  }
}
```

### Chat Endpoints

#### POST /chat/message
Send a message and get AI response.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "conv_12345",
  "user_id": "user_789",
  "provider": "gemini",
  "model": "gemini-pro",
  "model_parameters": {
    "temperature": 0.7,
    "max_tokens": 150
  }
}
```

**Response:**
```json
{
  "message": "Hello! I'm doing well, thank you for asking. How can I assist you today?",
  "conversation_id": "conv_12345",
  "message_id": "msg_67890",
  "model_used": "gemini-pro",
  "provider_used": "gemini",
  "tokens_used": 45,
  "processing_time": 1.2,
  "timestamp": "2023-10-09T15:30:00Z"
}
```

#### POST /chat/conversation
Start a new conversation.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "title": "My Chat Session",
  "initial_message": "Hello!"
}
```

#### GET /chat/conversation/{conversation_id}
Get conversation details and history.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "conversation_id": "conv_12345",
  "title": "My Chat Session",
  "created_at": "2023-10-09T15:00:00Z",
  "updated_at": "2023-10-09T15:30:00Z",
  "message_count": 6,
  "messages": [
    {
      "message_id": "msg_1",
      "role": "user",
      "content": "Hello!",
      "timestamp": "2023-10-09T15:00:00Z"
    },
    {
      "message_id": "msg_2",
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "timestamp": "2023-10-09T15:00:05Z"
    }
  ]
}
```

#### GET /chat/conversations
Get user's conversation list.

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `limit`: Number of conversations (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)

#### PUT /chat/conversation/{conversation_id}
Update conversation title or settings.

#### DELETE /chat/conversation/{conversation_id}
Delete a conversation.

### User Management Endpoints

#### GET /users/profile
Get user profile information.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "user_id": "user_12345",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2023-10-01T10:00:00Z",
  "last_login": "2023-10-09T15:00:00Z",
  "is_active": true,
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": true
  }
}
```

#### PUT /users/profile
Update user profile.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "full_name": "John Doe Jr.",
  "email": "john.jr@example.com"
}
```

#### GET /users/conversations/analytics
Get user's conversation analytics.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "total_conversations": 45,
  "total_messages": 234,
  "average_messages_per_conversation": 5.2,
  "most_active_day": "Monday",
  "conversation_topics": [
    {"topic": "programming", "count": 15},
    {"topic": "general", "count": 30}
  ],
  "monthly_usage": [
    {"month": "2023-09", "conversations": 20},
    {"month": "2023-10", "conversations": 25}
  ]
}
```

#### GET /users/preferences
Get user preferences.

#### PUT /users/preferences
Update user preferences.

**Request Body:**
```json
{
  "theme": "light",
  "language": "en",
  "notifications": false,
  "max_tokens": 200,
  "default_model": "gpt-4"
}
```

#### DELETE /users/account
Delete user account and all data.

### Gemini AI Provider Endpoints

All Gemini endpoints support provider management and AI model integration.

#### POST /gemini/register
Register and validate a Gemini API key (admin only).

**Headers:** `Authorization: Bearer <admin_secret_key>`

**Request Body:**
```json
{
  "api_key": "AIzaSyB...",
  "project_id": "my-gcp-project",
  "default_model": "gemini-pro",
  "description": "Production Gemini API key"
}
```

**Response:**
```json
{
  "message": "Gemini API key registered successfully",
  "registration_id": "gemini_reg_12345",
  "status": "valid",
  "default_model": "gemini-pro",
  "available_models": ["gemini-pro", "gemini-pro-vision"],
  "test_result": "API key is working",
  "registered_at": "2023-10-09T15:30:00Z"
}
```

#### GET /gemini/providers
Get list of available LLM providers and their status.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "available_providers": ["openai", "gemini"],
  "default_provider": "gemini",
  "provider_details": {
    "openai": {
      "name": "OpenAI",
      "models": ["gpt-4", "gpt-3.5-turbo"],
      "status": "configured",
      "features": ["chat", "completion", "streaming"]
    },
    "gemini": {
      "name": "Google Gemini", 
      "models": ["gemini-pro", "gemini-pro-vision"],
      "status": "configured",
      "features": ["chat", "completion", "vision"]
    }
  }
}
```

#### POST /gemini/test
Test a specific LLM provider with a message.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "message": "Hello, are you working?",
  "provider": "gemini",
  "model": "gemini-pro"
}
```

#### POST /gemini/configure
Configure LLM provider settings (admin only).

**Headers:** `Authorization: Bearer <admin_secret_key>`

**Request Body:**
```json
{
  "provider": "gemini",
  "model": "gemini-pro",
  "temperature": 0.8,
  "max_tokens": 1500,
  "is_default": true
}
```

#### GET /gemini/health
Check health status of all configured LLM providers.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "overall_status": "healthy",
  "providers": {
    "gemini": {
      "status": "healthy",
      "response_time": 1.23,
      "model": "gemini-pro"
    },
    "openai": {
      "status": "healthy", 
      "response_time": 0.89,
      "model": "gpt-3.5-turbo"
    }
  },
  "default_provider": "gemini",
  "default_provider_healthy": true
}
```

### Admin Endpoints

All admin endpoints require admin authorization:
```bash
Authorization: Bearer <admin_secret_key>
```

#### GET /admin/system/status
Get comprehensive system status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-09T15:30:00Z",
  "admin_info": {
    "settings": {
      "debug_mode": false,
      "log_level": "INFO",
      "api_version": "/api/v1"
    },
    "environment": {
      "app_name": "Chatbot API",
      "version": "1.0.0",
      "host": "0.0.0.0",
      "port": 8000
    }
  }
}
```

#### GET /admin/system/metrics
Get system usage metrics.

**Query Parameters:**
- `hours`: Hours of metrics to retrieve (1-168, default: 24)

**Response:**
```json
{
  "period": {
    "start": "2023-10-08T15:30:00Z",
    "end": "2023-10-09T15:30:00Z",
    "hours": 24
  },
  "api_metrics": {
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "average_response_time_ms": 245
  },
  "chat_metrics": {
    "total_messages": 890,
    "total_conversations": 156,
    "unique_users": 89
  },
  "llm_metrics": {
    "total_tokens_used": 45670,
    "model_usage": {
      "gpt-3.5-turbo": 0.85,
      "gpt-4": 0.15
    }
  }
}
```

#### GET /admin/users/overview
Get overview of all users.

**Query Parameters:**
- `limit`: Number of users (1-1000, default: 100)

#### POST /admin/system/maintenance
Trigger maintenance tasks.

**Query Parameters:**
- `task`: Task to execute (cleanup_logs, refresh_cache, health_check, etc.)

#### GET /admin/logs
Get system logs.

**Query Parameters:**
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `lines`: Number of lines (1-1000, default: 100)
- `service`: Service filter (optional)

#### PUT /admin/system/config
Update system configuration.

**Request Body:**
```json
{
  "log_level": "DEBUG",
  "rate_limit_per_minute": 120,
  "max_tokens": 4000
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2023-10-09T15:30:00Z"
}
```

### Common HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

## Rate Limiting

- **Default**: 60 requests per minute per user
- **Admin endpoints**: Higher limits
- **Rate limit headers** included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Data Models

### User Model
```json
{
  "user_id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_admin": "boolean",
  "is_active": "boolean",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

### Message Model
```json
{
  "message_id": "string",
  "conversation_id": "string",
  "role": "user|assistant",
  "content": "string",
  "timestamp": "datetime",
  "tokens_used": "integer",
  "model_used": "string"
}
```

### Conversation Model
```json
{
  "conversation_id": "string",
  "user_id": "string",
  "title": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "integer",
  "is_active": "boolean"
}
```

## WebSocket Support

Real-time chat functionality available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat/{conversation_id}?token={access_token}');

// Send message
ws.send(JSON.stringify({
  "type": "message",
  "content": "Hello!"
}));

// Receive responses
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(data.response);
};
```

## SDK Examples

### Python SDK
```python
import requests

# Authenticate
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'username': 'john_doe',
    'password': 'password123'
})
token = response.json()['access_token']

# Send chat message
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/v1/chat/message', 
    headers=headers,
    json={
        'message': 'Hello!',
        'conversation_id': 'conv_123'
    }
)
print(response.json()['response'])
```

### JavaScript SDK
```javascript
class ChatbotAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async sendMessage(message, conversationId) {
    const response = await fetch(`${this.baseURL}/api/v1/chat/message`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId
      })
    });
    return response.json();
  }
}

const api = new ChatbotAPI('http://localhost:8000', 'your_token');
api.sendMessage('Hello!', 'conv_123').then(console.log);
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key

# Optional
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
API_V1_STR=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  chatbot-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
```

For more information, visit the [GitHub repository](https://github.com/your-repo/chatbot-api) or contact support.