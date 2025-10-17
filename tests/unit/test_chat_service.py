"""
Unit tests for chat service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.chat_service import ChatService
from app.models.chat_models import ChatResponse, MessageRole


class TestChatService:
    """Test suite for ChatService."""
    
    def test_chat_service_initialization(self, chat_service):
        """Test ChatService initialization."""
        assert chat_service is not None
        assert hasattr(chat_service, 'llm_service')
        assert hasattr(chat_service, 'conversations')
        assert hasattr(chat_service, 'messages')
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, chat_service):
        """Test conversation creation."""
        user_id = "test_user_123"
        title = "Test Conversation"
        
        conversation = await chat_service.create_conversation(user_id, title)
        
        assert conversation.user_id == user_id
        assert conversation.title == title
        assert conversation.message_count == 0
        assert conversation.conversation_id.startswith("conv_")
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_empty(self, chat_service):
        """Test getting history for non-existent conversation."""
        history = await chat_service.get_conversation_history("nonexistent_conv")
        assert history == []
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, chat_service):
        """Test conversation deletion."""
        # Create a conversation first
        conversation = await chat_service.create_conversation("test_user")
        conv_id = conversation.conversation_id
        
        # Verify it exists
        assert conv_id in chat_service.conversations
        
        # Delete it
        result = await chat_service.delete_conversation(conv_id)
        assert result is True
        
        # Verify it's gone
        assert conv_id not in chat_service.conversations
    
    @pytest.mark.asyncio
    async def test_get_user_conversations(self, chat_service):
        """Test getting user conversations."""
        user_id = "test_user_456"
        
        # Create multiple conversations
        conv1 = await chat_service.create_conversation(user_id, "Conv 1")
        conv2 = await chat_service.create_conversation(user_id, "Conv 2")
        
        # Create conversation for different user
        await chat_service.create_conversation("other_user", "Other Conv")
        
        # Get conversations for test user
        conversations = await chat_service.get_user_conversations(user_id)
        
        assert len(conversations) == 2
        conv_ids = [c.conversation_id for c in conversations]
        assert conv1.conversation_id in conv_ids
        assert conv2.conversation_id in conv_ids
    
    @pytest.mark.asyncio
    @patch('app.services.chat_service.LLMService')
    async def test_process_message(self, mock_llm_service, chat_service):
        """Test message processing."""
        # Mock LLM service response
        mock_llm_response = {
            "message": "Hello! How can I help you?",
            "model_used": "gpt-3.5-turbo",
            "tokens_used": 25,
            "processing_time": 1.2
        }
        
        mock_llm_service.return_value.generate_chat_response.return_value = mock_llm_response
        chat_service.llm_service = mock_llm_service.return_value
        
        # Process a message
        response = await chat_service.process_message(
            message="Hello",
            user_id="test_user"
        )
        
        assert isinstance(response, ChatResponse)
        assert response.message == mock_llm_response["message"]
        assert response.model_used == mock_llm_response["model_used"]
        assert response.conversation_id is not None