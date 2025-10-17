"""
Chat endpoints for LLM chatbot interaction.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any
import logging

from app.models.chat_models import (
    ChatRequest, 
    ChatResponse, 
    ChatHistory, 
    ConversationCreate,
    ConversationResponse
)
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    chat_service: ChatService = Depends(ChatService),
    llm_service: LLMService = Depends(LLMService)
) -> ChatResponse:
    """
    Send a message to the chatbot and get a response.
    
    Args:
        request: Chat request containing message and optional conversation ID
        background_tasks: FastAPI background tasks for async operations
        chat_service: Chat service dependency
        llm_service: LLM service dependency
    
    Returns:
        ChatResponse with bot reply and metadata
    """
    try:
        # Process the chat message
        response = await chat_service.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            provider=request.provider,
            model=request.model
        )
        
        # Save conversation in background
        background_tasks.add_task(
            chat_service.save_conversation_async,
            request.conversation_id or response.conversation_id,
            request.message,
            response.message
        )
        
        logger.info(f"Chat message processed successfully for conversation {response.conversation_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@router.get("/history/{conversation_id}", response_model=List[ChatHistory])
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    chat_service: ChatService = Depends(ChatService)
) -> List[ChatHistory]:
    """
    Get conversation history for a specific conversation.
    
    Args:
        conversation_id: Unique conversation identifier
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        chat_service: Chat service dependency
    
    Returns:
        List of chat history entries
    """
    try:
        history = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        logger.info(f"Retrieved {len(history)} messages for conversation {conversation_id}")
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.post("/conversation", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    chat_service: ChatService = Depends(ChatService)
) -> ConversationResponse:
    """
    Create a new conversation.
    
    Args:
        request: Conversation creation request
        chat_service: Chat service dependency
    
    Returns:
        ConversationResponse with new conversation details
    """
    try:
        conversation = await chat_service.create_conversation(
            user_id=request.user_id,
            title=request.title
        )
        logger.info(f"New conversation created: {conversation.conversation_id}")
        return conversation
        
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, str]:
    """
    Delete a conversation and its history.
    
    Args:
        conversation_id: Unique conversation identifier
        chat_service: Chat service dependency
    
    Returns:
        Success message
    """
    try:
        await chat_service.delete_conversation(conversation_id)
        logger.info(f"Conversation deleted: {conversation_id}")
        return {"message": f"Conversation {conversation_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")


@router.get("/conversations/{user_id}", response_model=List[ConversationResponse])
async def get_user_conversations(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    chat_service: ChatService = Depends(ChatService)
) -> List[ConversationResponse]:
    """
    Get all conversations for a specific user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        chat_service: Chat service dependency
    
    Returns:
        List of user conversations
    """
    try:
        conversations = await chat_service.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
        return conversations
        
    except Exception as e:
        logger.error(f"Error retrieving user conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")