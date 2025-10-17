"""
Test cases for Gemini API integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider, GeminiService
from app.models.chat_models import LLMConfig


class TestGeminiService:
    """Test cases for Gemini service functionality."""
    
    @pytest.mark.asyncio
    async def test_gemini_service_initialization(self):
        """Test Gemini service can be initialized."""
        api_key = "test_api_key"
        service = GeminiService(api_key)
        assert service.api_key == api_key
        assert service._client is None
    
    @pytest.mark.asyncio
    async def test_gemini_message_conversion(self):
        """Test message format conversion for Gemini."""
        service = GeminiService("test_key")
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        prompt = service._convert_messages_to_prompt(messages)
        
        expected_parts = [
            "System: You are a helpful assistant",
            "User: Hello", 
            "Assistant: Hi there!",
            "User: How are you?"
        ]
        
        for part in expected_parts:
            assert part in prompt
        assert prompt.endswith("Assistant:")


class TestEnhancedLLMService:
    """Test cases for Enhanced LLM service."""
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        providers = enhanced_llm_service.get_available_providers()
        assert isinstance(providers, list)
        # Should include available providers based on configuration
    
    @pytest.mark.asyncio
    async def test_list_available_models(self):
        """Test listing available models for each provider."""
        openai_models = await enhanced_llm_service.list_available_models(LLMProvider.OPENAI)
        assert "gpt-3.5-turbo" in openai_models
        assert "gpt-4" in openai_models
        
        gemini_models = await enhanced_llm_service.list_available_models(LLMProvider.GEMINI)
        assert "gemini-2.5-flash" in gemini_models or "gemini-2.5-flash" in gemini_models
    
    @pytest.mark.asyncio
    async def test_provider_health_check(self):
        """Test provider health check functionality."""
        # Test with mock to avoid actual API calls
        with patch.object(enhanced_llm_service, 'generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = {
                "response": "OK",
                "model": "test-model",
                "provider": "test",
                "tokens_used": 5,
                "response_time": 0.5
            }
            
            result = await enhanced_llm_service.test_provider_connection(LLMProvider.OPENAI)
            assert result["status"] == "healthy"
            assert "response_time" in result


class TestGeminiEndpoints:
    """Test cases for Gemini API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from main import app
        return TestClient(app)
    
    def test_get_providers_endpoint(self, client, mock_auth_user):
        """Test the providers endpoint."""
        with patch('app.utils.auth.get_current_user', return_value=mock_auth_user):
            response = client.get("/api/v1/gemini/providers")
            assert response.status_code == 200
            
            data = response.json()
            assert "available_providers" in data
            assert "provider_details" in data
    
    def test_gemini_registration_endpoint(self, client, mock_admin_user, sample_gemini_registration):
        """Test Gemini API registration endpoint."""
        with patch('app.utils.auth.get_current_admin_user', return_value=mock_admin_user):
            with patch('app.services.enhanced_llm_service.GeminiService') as mock_service:
                # Mock successful API key test
                mock_instance = Mock()
                mock_instance.generate_response = AsyncMock(return_value={
                    "response": "API key is working",
                    "model": "gemini-2.5-flash",
                    "tokens_used": 10
                })
                mock_service.return_value = mock_instance
                
                response = client.post(
                    "/api/v1/gemini/register",
                    json=sample_gemini_registration
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Gemini API key registered successfully"
                assert "registration_id" in data
    
    def test_test_provider_endpoint(self, client, mock_auth_user):
        """Test the provider testing endpoint."""
        test_data = {
            "message": "Hello, test!",
            "provider": "gemini",
            "model": "gemini-2.5-flash"
        }
        
        with patch('app.utils.auth.get_current_user', return_value=mock_auth_user):
            with patch.object(enhanced_llm_service, 'generate_response', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = {
                    "response": "Hello! Test successful.",
                    "model": "gemini-2.5-flash",
                    "provider": "gemini",
                    "tokens_used": 15,
                    "response_time": 1.2,
                    "finish_reason": "stop"
                }
                
                response = client.post("/api/v1/gemini/test", json=test_data)
                assert response.status_code == 200
                
                data = response.json()
                assert data["provider"] == "gemini"
                assert data["response"] == "Hello! Test successful."
                assert "performance" in data


class TestChatWithGemini:
    """Test cases for chat functionality with Gemini."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from main import app
        return TestClient(app)
    
    def test_chat_message_with_gemini(self, client, mock_auth_user, sample_chat_request):
        """Test sending a chat message with Gemini provider."""
        with patch('app.utils.auth.get_current_user', return_value=mock_auth_user):
            with patch('app.services.chat_service.ChatService.process_message', new_callable=AsyncMock) as mock_process:
                mock_process.return_value = Mock(
                    message="Hello! I'm Gemini AI assistant.",
                    conversation_id="conv_test123",
                    message_id="msg_test456",
                    model_used="gemini-2.5-flash",
                    provider_used="gemini",
                    tokens_used=25,
                    processing_time=1.5
                )
                
                response = client.post("/api/v1/chat/message", json=sample_chat_request)
                assert response.status_code == 200
                
                # Verify the correct parameters were passed
                mock_process.assert_called_once()
                call_args = mock_process.call_args
                assert call_args.kwargs["provider"] == "gemini"
                assert call_args.kwargs["model"] == "gemini-2.5-flash"
    
    @pytest.mark.asyncio
    async def test_chat_service_with_provider_selection(self, mock_gemini_response):
        """Test chat service with provider selection."""
        from app.services.chat_service import ChatService
        
        chat_service = ChatService()
        
        with patch.object(enhanced_llm_service, 'generate_response', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_gemini_response
            
            response = await chat_service.process_message(
                message="Hello!",
                user_id="test_user",
                provider="gemini",
                model="gemini-2.5-flash"
            )
            
            # Verify the response
            assert response.provider_used == "gemini"
            assert response.model_used == "gemini-2.5-flash"
            assert response.message == mock_gemini_response["response"]
            
            # Verify the correct provider was called
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert call_args.kwargs["provider"] == LLMProvider.GEMINI


class TestGeminiConfiguration:
    """Test cases for Gemini configuration."""
    
    def test_gemini_model_configuration(self):
        """Test Gemini model configuration."""
        from config.settings import settings
        
        # Test that Gemini settings are properly configured
        assert hasattr(settings, 'gemini_api_key')
        assert hasattr(settings, 'gemini_model')
        assert hasattr(settings, 'default_llm_provider')
    
    def test_llm_config_with_gemini(self):
        """Test LLM configuration with Gemini models."""
        config = LLMConfig(
            model="gemini-2.5-flash",
            temperature=0.8,
            max_tokens=1500
        )
        
        assert config.model == "gemini-2.5-flash"
        assert config.temperature == 0.8
        assert config.max_tokens == 1500


class TestErrorHandling:
    """Test error handling in Gemini integration."""
    
    @pytest.mark.asyncio
    async def test_invalid_api_key_handling(self):
        """Test handling of invalid API key."""
        service = GeminiService("invalid_key")
        
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model.side_effect = Exception("Invalid API key")
            
            with pytest.raises(Exception) as exc_info:
                await service.generate_response(
                    messages=[{"role": "user", "content": "test"}],
                    model="gemini-2.5-flash"
                )
            
            assert "Invalid API key" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_quota_exceeded_handling(self):
        """Test handling of quota exceeded error."""
        service = GeminiService("valid_key")
        
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_instance = Mock()
            mock_instance.generate_content.side_effect = Exception("Quota exceeded")
            mock_model.return_value = mock_instance
            
            with pytest.raises(Exception) as exc_info:
                await service.generate_response(
                    messages=[{"role": "user", "content": "test"}],
                    model="gemini-2.5-flash"
                )
            
            assert "Quota exceeded" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_provider_fallback(self):
        """Test provider fallback when one fails."""
        messages = [{"role": "user", "content": "Hello"}]
        
        with patch.object(enhanced_llm_service, '_generate_gemini_response', side_effect=Exception("Gemini failed")):
            with patch.object(enhanced_llm_service, '_generate_openai_response', new_callable=AsyncMock) as mock_openai:
                mock_openai.return_value = {
                    "response": "Hello from OpenAI fallback",
                    "model": "gpt-3.5-turbo",
                    "provider": "openai",
                    "tokens_used": 20
                }
                
                # Test that it falls back to available provider
                providers = enhanced_llm_service.get_available_providers()
                if "openai" in providers:
                    result = await enhanced_llm_service.generate_response(
                        messages=messages,
                        provider=LLMProvider.OPENAI
                    )
                    assert result["provider"] == "openai"