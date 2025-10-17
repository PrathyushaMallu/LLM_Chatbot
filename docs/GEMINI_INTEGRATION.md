# Gemini API Integration Guide

## Overview

This guide explains how to integrate Google's Gemini AI API with the chatbot system, providing an alternative to OpenAI's GPT models.

## Features

- **Multi-Provider Support**: Switch between OpenAI and Gemini providers
- **Dynamic Provider Selection**: Choose provider per conversation or message
- **Provider Health Monitoring**: Real-time status checks for all providers
- **Unified API Interface**: Same endpoints work with both providers
- **Automatic Fallback**: Graceful handling when primary provider is unavailable

## Quick Setup

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key (starts with 'AIza...')

### 2. Configure Environment

Add to your `.env` file:
```bash
# Google Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro
DEFAULT_LLM_PROVIDER=gemini  # or openai
```

### 3. Install Dependencies

```bash
pip install google-generativeai==0.3.2
```

## API Endpoints

### Register Gemini API

**POST** `/api/v1/gemini/register`

Register and validate a Gemini API key.

```bash
curl -X POST "http://localhost:8000/api/v1/gemini/register" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "AIza...",
    "default_model": "gemini-pro",
    "description": "Production Gemini API key"
  }'
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
  "registered_at": "2023-10-12T19:30:00Z",
  "next_steps": [
    "Set Gemini as default provider in system settings",
    "Configure model preferences", 
    "Test with chat endpoints"
  ]
}
```

### Get Available Providers

**GET** `/api/v1/gemini/providers`

List all configured LLM providers and their status.

```bash
curl -X GET "http://localhost:8000/api/v1/gemini/providers" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

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
      "default_model": "gpt-3.5-turbo",
      "features": ["chat", "completion", "streaming"]
    },
    "gemini": {
      "name": "Google Gemini",
      "models": ["gemini-pro", "gemini-pro-vision"],
      "status": "configured", 
      "default_model": "gemini-pro",
      "features": ["chat", "completion", "vision"]
    }
  }
}
```

### Test Provider

**POST** `/api/v1/gemini/test`

Test a specific provider with a message.

```bash
curl -X POST "http://localhost:8000/api/v1/gemini/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, are you working?",
    "provider": "gemini",
    "model": "gemini-pro"
  }'
```

**Response:**
```json
{
  "test_message": "Hello, are you working?",
  "provider": "gemini",
  "model": "gemini-pro",
  "response": "Yes, I'm working perfectly! How can I help you?",
  "performance": {
    "response_time_seconds": 1.23,
    "tokens_used": 45,
    "finish_reason": "stop"
  },
  "test_metadata": {
    "user_id": "user_12345",
    "tested_at": "2023-10-12T19:30:00Z",
    "provider_status": "working"
  }
}
```

### Configure Provider

**POST** `/api/v1/gemini/configure`

Configure provider settings (admin only).

```bash
curl -X POST "http://localhost:8000/api/v1/gemini/configure" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "model": "gemini-pro",
    "temperature": 0.8,
    "max_tokens": 1500,
    "is_default": true
  }'
```

### Check Provider Health

**GET** `/api/v1/gemini/health`

Check health status of all providers.

```bash
curl -X GET "http://localhost:8000/api/v1/gemini/health" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Using Gemini in Chat

### Basic Chat with Gemini

**POST** `/api/v1/chat/message`

```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing",
    "user_id": "user_123",
    "provider": "gemini",
    "model": "gemini-pro",
    "model_parameters": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }'
```

**Response:**
```json
{
  "message": "Quantum computing is a revolutionary computing paradigm...",
  "conversation_id": "conv_abc123",
  "message_id": "msg_def456",
  "timestamp": "2023-10-12T19:30:00Z",
  "model_used": "gemini-pro",
  "provider_used": "gemini",
  "tokens_used": 234,
  "processing_time": 1.45
}
```

### Provider Comparison

Test the same message with different providers:

```bash
# Test with OpenAI
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -d '{"message": "Explain AI", "provider": "openai", "user_id": "user_123"}'

# Test with Gemini  
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -d '{"message": "Explain AI", "provider": "gemini", "user_id": "user_123"}'
```

## Available Models

### Gemini Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `gemini-pro` | General purpose model | Text generation, chat, analysis |
| `gemini-pro-vision` | Multimodal model | Image analysis, vision tasks |

### OpenAI Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `gpt-4` | Most capable model | Complex reasoning, creative tasks |
| `gpt-3.5-turbo` | Fast and efficient | General chat, quick responses |

## Configuration Examples

### Environment Variables

```bash
# Use Gemini as default
DEFAULT_LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyB...
GEMINI_MODEL=gemini-pro

# Use OpenAI as default  
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Both providers configured
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIzaSyB...
DEFAULT_LLM_PROVIDER=gemini
```

### Python Configuration

```python
from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider
from app.models.chat_models import LLMConfig

# Generate response with Gemini
messages = [{"role": "user", "content": "Hello!"}]
config = LLMConfig(model="gemini-pro", temperature=0.8)

response = await enhanced_llm_service.generate_response(
    messages=messages,
    provider=LLMProvider.GEMINI,
    config=config
)

print(response["response"])
```

## Error Handling

### Common Errors

**Invalid API Key:**
```json
{
  "detail": "Invalid Gemini API key: API key not valid. Please pass a valid API key.",
  "status_code": 400
}
```

**Provider Not Available:**
```json
{
  "detail": "Provider 'gemini' not configured",
  "status_code": 500
}
```

**Rate Limit Exceeded:**
```json
{
  "detail": "Rate limit exceeded for Gemini API",
  "status_code": 429
}
```

### Retry Logic

```python
import asyncio
from app.services.enhanced_llm_service import enhanced_llm_service

async def robust_generate(messages, max_retries=3):
    for provider in [LLMProvider.GEMINI, LLMProvider.OPENAI]:
        for attempt in range(max_retries):
            try:
                return await enhanced_llm_service.generate_response(
                    messages=messages,
                    provider=provider
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    continue  # Try next provider
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    raise Exception("All providers failed")
```

## Monitoring and Analytics

### Provider Performance Metrics

```bash
# Get system metrics including provider usage
curl -X GET "http://localhost:8000/api/v1/admin/system/metrics?hours=24" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Health Monitoring

```bash
# Automated health check
curl -X GET "http://localhost:8000/api/v1/gemini/health" | jq '.overall_status'
```

### Usage Analytics

Track provider usage in your application:

```python
# Log provider usage
logger.info(f"Provider used: {response['provider']}, "
           f"Model: {response['model']}, "
           f"Tokens: {response['tokens_used']}, "
           f"Time: {response['response_time']}")
```

## Best Practices

### 1. Provider Selection Strategy

```python
def select_provider(task_type, user_preferences):
    if task_type == "creative_writing":
        return LLMProvider.OPENAI, "gpt-4"
    elif task_type == "general_chat":
        return LLMProvider.GEMINI, "gemini-pro"
    elif task_type == "image_analysis":
        return LLMProvider.GEMINI, "gemini-pro-vision"
    else:
        return LLMProvider(user_preferences.get("default_provider", "openai"))
```

### 2. Cost Optimization

- Use Gemini for general queries (often less expensive)
- Use OpenAI for specialized tasks requiring high accuracy
- Monitor token usage and implement limits

### 3. Fallback Strategy

```python
PROVIDER_PRIORITY = [
    (LLMProvider.GEMINI, "gemini-pro"),
    (LLMProvider.OPENAI, "gpt-3.5-turbo"),
    (LLMProvider.OPENAI, "gpt-4")
]

async def generate_with_fallback(messages):
    for provider, model in PROVIDER_PRIORITY:
        try:
            config = LLMConfig(model=model)
            return await enhanced_llm_service.generate_response(
                messages=messages,
                provider=provider,
                config=config
            )
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
    raise Exception("All providers exhausted")
```

## Troubleshooting

### Common Issues

1. **API Key Format Error**
   - Ensure Gemini key starts with 'AIza' or 'ya29'
   - Check for extra spaces or characters

2. **Import Error**
   - Install: `pip install google-generativeai`
   - Verify version: `pip show google-generativeai`

3. **Provider Not Loading**
   - Check environment variables are set
   - Restart the application after config changes

4. **Permission Denied**
   - Verify API key has correct permissions
   - Check Google Cloud project settings

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

### Testing Script

Run the included test script:

```bash
python scripts/test_gemini.py
```

## Integration Examples

### Streamlit Frontend

```python
import streamlit as st
import requests

# Provider selection
provider = st.selectbox("Select AI Provider", ["openai", "gemini"])
model = st.selectbox("Select Model", 
    ["gpt-3.5-turbo", "gpt-4"] if provider == "openai" 
    else ["gemini-pro", "gemini-pro-vision"]
)

# Send message
if st.button("Send"):
    response = requests.post("http://localhost:8000/api/v1/chat/message", 
        json={
            "message": user_input,
            "provider": provider,
            "model": model,
            "user_id": "streamlit_user"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    st.write(response.json()["message"])
```

### React Frontend

```javascript
const sendMessage = async (message, provider = 'gemini') => {
  const response = await fetch('/api/v1/chat/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      provider,
      model: provider === 'gemini' ? 'gemini-pro' : 'gpt-3.5-turbo',
      user_id: userId
    })
  });
  
  return response.json();
};
```

For more examples and updates, see the [main API documentation](API_COMPREHENSIVE.md).