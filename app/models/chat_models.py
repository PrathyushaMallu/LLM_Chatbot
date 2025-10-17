"""
Pydantic models for chat functionality.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., description="User message", min_length=1, max_length=4000)
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    user_id: str = Field(..., description="User identifier")
    provider: Optional[str] = Field("openai", description="LLM provider (openai/gemini)")
    model: Optional[str] = Field(None, description="Specific model to use")
    model_parameters: Optional[Dict[str, Any]] = Field(None, description="Optional LLM parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "conversation_id": "conv_123456",
                "user_id": "user_789",
                "provider": "gemini",
                "model": "gemini-pro",
                "model_parameters": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    message: str = Field(..., description="Assistant response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    message_id: str = Field(..., description="Unique message identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    model_used: str = Field(..., description="LLM model used for response")
    provider_used: str = Field(..., description="LLM provider used for response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    processing_time: Optional[float] = Field(None, description="Response processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "conversation_id": "conv_123456",
                "message_id": "msg_789012",
                "timestamp": "2023-10-09T10:30:00Z",
                "model_used": "gpt-3.5-turbo",
                "tokens_used": 25,
                "processing_time": 1.2
            }
        }


class ChatHistory(BaseModel):
    """Model for chat history entries."""
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Conversation identifier")
    role: MessageRole = Field(..., description="Message role (user/assistant)")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    tokens_used: Optional[int] = Field(None, description="Tokens used for this message")
    model_used: Optional[str] = Field(None, description="Model used (for assistant messages)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_123456",
                "conversation_id": "conv_789012",
                "role": "user",
                "message": "What is the weather like today?",
                "timestamp": "2023-10-09T10:29:00Z",
                "tokens_used": 8,
                "model_used": None
            }
        }


class ConversationCreate(BaseModel):
    """Model for creating new conversations."""
    user_id: str = Field(..., description="User identifier")
    title: Optional[str] = Field(None, description="Optional conversation title", max_length=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "title": "Discussion about AI"
            }
        }


class ConversationResponse(BaseModel):
    """Response model for conversation information."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: str = Field(..., description="User identifier")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages in conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123456",
                "user_id": "user_789",
                "title": "AI Discussion",
                "created_at": "2023-10-09T10:00:00Z",
                "updated_at": "2023-10-09T10:30:00Z",
                "message_count": 10
            }
        }


class LLMConfig(BaseModel):
    """Configuration model for LLM parameters."""
    model: str = Field("gpt-3.5-turbo", description="LLM model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Response creativity (0-2)")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum tokens in response")
    top_p: float = Field(1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float = Field(0.0, ge=-2.0, le=2.0, description="Presence penalty")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        }