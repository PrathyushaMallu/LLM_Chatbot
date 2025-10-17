"""
Test configuration and fixtures.
"""

import pytest
import asyncio
import sys
import os
from typing import Generator
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.chat_service import ChatService
from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider
from app.services.health_service import HealthService


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a mock response from the chatbot."
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = Mock()
    mock_response.usage.total_tokens = 25
    return mock_response


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "response": "This is a mock response from Gemini.",
        "model": "gemini-2.5-flash",
        "provider": "gemini",
        "tokens_used": 30,
        "response_time": 1.23,
        "timestamp": "2023-10-12T19:30:00Z",
        "finish_reason": "stop"
    }


@pytest.fixture
def mock_llm_response():
    """Mock enhanced LLM service response."""
    return {
        "response": "This is a mock LLM response.",
        "model": "test-model",
        "provider": "test-provider",
        "tokens_used": 25,
        "response_time": 1.0,
        "timestamp": "2023-10-12T19:30:00Z",
        "finish_reason": "stop"
    }


@pytest.fixture
def chat_service():
    """Create a ChatService instance for testing."""
    return ChatService()


@pytest.fixture
def llm_service():
    """Create an Enhanced LLM Service instance for testing."""
    return enhanced_llm_service


@pytest.fixture
def health_service():
    """Create a HealthService instance for testing."""
    return HealthService()


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "conversation_id": "conv_test123",
        "user_id": "user_test456",
        "title": "Test Conversation",
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test message"
            },
            {
                "role": "assistant", 
                "content": "Hello! This is a test response."
            }
        ]
    }


@pytest.fixture
def sample_gemini_registration():
    """Sample Gemini registration data for testing."""
    return {
        "api_key": "AIzaSyTest123...",
        "project_id": "test-project-id",
        "default_model": "gemini-2.5-flash",
        "description": "Test Gemini API key"
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat request data for testing."""
    return {
        "message": "Hello, how are you?",
        "user_id": "user_test123",
        "conversation_id": "conv_test456",
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "model_parameters": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for testing."""
    return {
        "user_id": "user_test123",
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing."""
    return {
        "user_id": "admin_test123",
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True
    }