"""
Chat service for managing conversations and chat logic.
"""

import asyncio
import uuid
import logging
import sys
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models.chat_models import (
    ChatResponse, 
    ChatHistory, 
    ConversationResponse, 
    MessageRole,
    LLMConfig
)
from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider


class ChatService:
    """Service for managing chat conversations and interactions."""
    
    def __init__(self):
        """Initialize chat service."""
        self.logger = logging.getLogger(__name__)
        self.llm_service = enhanced_llm_service
        
        # In-memory storage for demonstration
        # In production, use a proper database
        self.conversations: Dict[str, Dict] = {}
        self.messages: Dict[str, List[Dict]] = {}
    
    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_id: str = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[LLMConfig] = None
    ) -> ChatResponse:
        """
        Process a chat message and generate response.
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            user_id: User identifier
            provider: LLM provider to use (openai/gemini)
            model: Specific model to use
            config: Optional LLM configuration
        
        Returns:
            ChatResponse with bot reply and metadata
        """
        try:
            # Create conversation if it doesn't exist
            if not conversation_id:
                conversation_id = await self._create_conversation_id(user_id)
            
            # Get conversation history
            history = await self.get_conversation_history(
                conversation_id, 
                limit=10  # Keep recent context
            )
            
            # Convert history to LLM format
            llm_history = []
            for hist in history:
                llm_history.append({
                    "role": hist.role.value,
                    "content": hist.message
                })
            
            # Add user message to history
            llm_history.append({
                "role": "user",
                "content": message
            })
            
            # Determine provider and model
            llm_provider = None
            if provider:
                llm_provider = LLMProvider(provider)
            
            # Create config if model specified
            if model and config is None:
                from config.settings import settings
                config = LLMConfig(
                    model=model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens
                )
            
            # Generate response (try provider, but fall back to local on error)
            try:
                llm_response = await self.llm_service.generate_response(
                    messages=llm_history,
                    provider=llm_provider,
                    config=config
                )
            except Exception as e:
                # Log and fallback to local responder so API remains usable
                self.logger.exception(f"LLM provider failed, falling back to local responder: {e}")
                llm_response = await self.llm_service._generate_local_response(llm_history, config)
            
            # Create message IDs
            user_message_id = str(uuid.uuid4())
            assistant_message_id = str(uuid.uuid4())
            
            # Store user message
            await self._store_message(
                conversation_id=conversation_id,
                message_id=user_message_id,
                role=MessageRole.USER,
                message=message,
                user_id=user_id
            )
            
            # Store assistant message
            await self._store_message(
                conversation_id=conversation_id,
                message_id=assistant_message_id,
                role=MessageRole.ASSISTANT,
                message=llm_response["response"],
                model_used=llm_response["model"],
                tokens_used=llm_response["tokens_used"]
            )
            
            # Create response
            response = ChatResponse(
                message=llm_response["response"],
                conversation_id=conversation_id,
                message_id=assistant_message_id,
                timestamp=datetime.utcnow(),
                model_used=llm_response["model"],
                provider_used=llm_response["provider"],
                tokens_used=llm_response["tokens_used"],
                processing_time=llm_response["processing_time"]
            )
            
            self.logger.info(f"Message processed successfully for conversation {conversation_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise
    
    async def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatHistory]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages
            offset: Number of messages to skip
        
        Returns:
            List of chat history entries
        """
        if conversation_id not in self.messages:
            return []
        
        messages = self.messages[conversation_id]
        
        # Apply offset and limit
        start_idx = offset
        end_idx = start_idx + limit
        
        history = []
        for msg in messages[start_idx:end_idx]:
            history.append(ChatHistory(**msg))
        
        return history
    
    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> ConversationResponse:
        """
        Create a new conversation.
        
        Args:
            user_id: User identifier
            title: Optional conversation title
        
        Returns:
            ConversationResponse with conversation details
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        conversation_data = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "title": title or f"Conversation {timestamp.strftime('%Y-%m-%d %H:%M')}",
            "created_at": timestamp,
            "updated_at": timestamp,
            "message_count": 0
        }
        
        self.conversations[conversation_id] = conversation_data
        self.messages[conversation_id] = []
        
        self.logger.info(f"Created new conversation: {conversation_id}")
        
        return ConversationResponse(**conversation_data)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and its history.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            True if deleted successfully
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        
        if conversation_id in self.messages:
            del self.messages[conversation_id]
        
        self.logger.info(f"Deleted conversation: {conversation_id}")
        return True
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[ConversationResponse]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of conversations
            offset: Number of conversations to skip
        
        Returns:
            List of user conversations
        """
        user_conversations = [
            conv for conv in self.conversations.values()
            if conv["user_id"] == user_id
        ]
        
        # Sort by updated_at descending
        user_conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        
        # Apply offset and limit
        start_idx = offset
        end_idx = start_idx + limit
        
        return [
            ConversationResponse(**conv)
            for conv in user_conversations[start_idx:end_idx]
        ]
    
    async def save_conversation_async(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str
    ):
        """
        Background task to save conversation data.
        
        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            assistant_message: Assistant's response
        """
        try:
            # Update conversation timestamp
            if conversation_id in self.conversations:
                self.conversations[conversation_id]["updated_at"] = datetime.utcnow()
                self.conversations[conversation_id]["message_count"] += 2
            
            self.logger.info(f"Conversation saved asynchronously: {conversation_id}")
            
        except Exception as e:
            self.logger.error(f"Error saving conversation: {str(e)}")
    
    async def _create_conversation_id(self, user_id: str) -> str:
        """Create a new conversation for the user."""
        conversation = await self.create_conversation(user_id)
        return conversation.conversation_id
    
    async def _store_message(
        self,
        conversation_id: str,
        message_id: str,
        role: MessageRole,
        message: str,
        user_id: str = None,
        model_used: str = None,
        tokens_used: int = None
    ):
        """Store a message in the conversation."""
        if conversation_id not in self.messages:
            self.messages[conversation_id] = []
        
        message_data = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "message": message,
            "timestamp": datetime.utcnow(),
            "tokens_used": tokens_used,
            "model_used": model_used
        }
        
        self.messages[conversation_id].append(message_data)