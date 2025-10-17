# API Documentation

## Overview

This document provides detailed information about the LLM Chatbot API endpoints, data models, and usage examples.

## Base URL

- Development: `http://localhost:8000`
- API Base Path: `/api/v1`

## Authentication

Currently, the API does not require authentication for development. In production, implement proper authentication mechanisms.

## Error Handling

All API endpoints return standardized error responses:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "timestamp": "2023-10-09T10:30:00Z"
}
```

## Health Endpoints

### Get Health Status
Get comprehensive system health information.

**Endpoint:** `GET /api/v1/health/`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-10-09T10:30:00Z",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "app_name": "LLM Chatbot",
  "checks": {
    "llm_service": {
      "status": "healthy",
      "details": "OpenAI API connection"
    },
    "database": {
      "status": "healthy", 
      "details": "Database connection OK"
    },
    "memory": {
      "status": "healthy",
      "details": "Memory usage: 45.2%",
      "used_gb": 2.1,
      "total_gb": 4.0
    }
  },
  "response_time_ms": 150
}
```

### Readiness Probe
Check if the application is ready to serve requests.

**Endpoint:** `GET /api/v1/health/readiness`

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2023-10-09T10:30:00Z",
  "checks": [
    {
      "name": "llm_service",
      "ready": true,
      "message": "LLM service available"
    },
    {
      "name": "configuration",
      "ready": true,
      "message": "Configuration OK"
    }
  ]
}
```

## Chat Endpoints

### Send Message
Send a message to the chatbot and receive a response.

**Endpoint:** `POST /api/v1/chat/message`

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "conv_123456789abc",
  "user_id": "user_789",
  "model_parameters": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**Response:**
```json
{
  "message": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "conversation_id": "conv_123456789abc",
  "message_id": "msg_987654321def",
  "timestamp": "2023-10-09T10:30:00Z",
  "model_used": "gpt-3.5-turbo",
  "tokens_used": 25,
  "processing_time": 1.2
}
```

### Get Conversation History
Retrieve the history of messages for a specific conversation.

**Endpoint:** `GET /api/v1/chat/history/{conversation_id}`

**Query Parameters:**
- `limit` (optional): Maximum number of messages (default: 50)
- `offset` (optional): Number of messages to skip (default: 0)

**Response:**
```json
[
  {
    "message_id": "msg_123456",
    "conversation_id": "conv_789012",
    "role": "user",
    "message": "What is the weather like today?",
    "timestamp": "2023-10-09T10:29:00Z",
    "tokens_used": 8,
    "model_used": null
  },
  {
    "message_id": "msg_123457",
    "conversation_id": "conv_789012",
    "role": "assistant",
    "message": "I don't have access to real-time weather data...",
    "timestamp": "2023-10-09T10:29:05Z",
    "tokens_used": 45,
    "model_used": "gpt-3.5-turbo"
  }
]
```

### Create Conversation
Create a new conversation.

**Endpoint:** `POST /api/v1/chat/conversation`

**Request Body:**
```json
{
  "user_id": "user_123",
  "title": "Discussion about AI"
}
```

**Response:**
```json
{
  "conversation_id": "conv_123456789abc",
  "user_id": "user_123",
  "title": "Discussion about AI",
  "created_at": "2023-10-09T10:00:00Z",
  "updated_at": "2023-10-09T10:00:00Z",
  "message_count": 0
}
```

### Delete Conversation
Delete a conversation and its entire history.

**Endpoint:** `DELETE /api/v1/chat/conversation/{conversation_id}`

**Response:**
```json
{
  "message": "Conversation conv_123456789abc deleted successfully"
}
```

### Get User Conversations
Get all conversations for a specific user.

**Endpoint:** `GET /api/v1/chat/conversations/{user_id}`

**Query Parameters:**
- `limit` (optional): Maximum number of conversations (default: 20)
- `offset` (optional): Number of conversations to skip (default: 0)

**Response:**
```json
[
  {
    "conversation_id": "conv_123456789abc",
    "user_id": "user_123",
    "title": "AI Discussion",
    "created_at": "2023-10-09T10:00:00Z",
    "updated_at": "2023-10-09T10:30:00Z",
    "message_count": 10
  }
]
```

## Data Models

### ChatRequest
```json
{
  "message": "string (required, 1-4000 chars)",
  "conversation_id": "string (optional)",
  "user_id": "string (required)",
  "model_parameters": {
    "temperature": "float (0-2, optional)",
    "max_tokens": "int (1-4000, optional)"
  }
}
```

### ChatResponse
```json
{
  "message": "string",
  "conversation_id": "string",
  "message_id": "string",
  "timestamp": "datetime",
  "model_used": "string",
  "tokens_used": "int (optional)",
  "processing_time": "float (optional)"
}
```

### LLMConfig
```json
{
  "model": "string (default: gpt-3.5-turbo)",
  "temperature": "float (0-2, default: 0.7)",
  "max_tokens": "int (1-4000, default: 1000)",
  "top_p": "float (0-1, default: 1.0)",
  "frequency_penalty": "float (-2 to 2, default: 0.0)",
  "presence_penalty": "float (-2 to 2, default: 0.0)"
}
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:8000/api/v1"

# Send a chat message
def send_message(message, user_id, conversation_id=None):
    payload = {
        "message": message,
        "user_id": user_id,
        "conversation_id": conversation_id
    }
    
    response = requests.post(
        f"{base_url}/chat/message",
        json=payload
    )
    
    return response.json()

# Example usage
response = send_message("Hello!", "user_123")
print(f"Bot: {response['message']}")
print(f"Conversation ID: {response['conversation_id']}")
```

### JavaScript Client Example

```javascript
// Send a chat message
async function sendMessage(message, userId, conversationId = null) {
    const payload = {
        message: message,
        user_id: userId,
        conversation_id: conversationId
    };
    
    const response = await fetch('http://localhost:8000/api/v1/chat/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// Example usage
sendMessage("Hello!", "user_123")
    .then(response => {
        console.log("Bot:", response.message);
        console.log("Conversation ID:", response.conversation_id);
    });
```

### cURL Examples

```bash
# Send a message
curl -X POST "http://localhost:8000/api/v1/chat/message" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "user_id": "user_123"
     }'

# Get conversation history
curl -X GET "http://localhost:8000/api/v1/chat/history/conv_123456789abc?limit=10"

# Create a new conversation
curl -X POST "http://localhost:8000/api/v1/chat/conversation" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user_123",
       "title": "My Chat Session"
     }'

# Health check
curl -X GET "http://localhost:8000/api/v1/health/"
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Default**: 60 requests per minute per IP
- **Headers**: Rate limit information is included in response headers
- **Exceeded**: Returns HTTP 429 with retry information

## Error Codes

- **400**: Bad Request - Invalid input data
- **404**: Not Found - Resource not found
- **422**: Validation Error - Request validation failed
- **429**: Too Many Requests - Rate limit exceeded
- **500**: Internal Server Error - Server-side error
- **503**: Service Unavailable - LLM service unavailable

## WebSocket Support (Future)

WebSocket endpoints for real-time chat will be available:
- `ws://localhost:8000/ws/chat/{conversation_id}`

## Versioning

The API uses URL versioning:
- Current version: `v1`
- Base path: `/api/v1`
- Future versions will be available at `/api/v2`, etc.

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json