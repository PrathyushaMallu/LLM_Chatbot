"""
User management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.models.chat_models import ConversationResponse
from app.services.chat_service import ChatService
from app.utils.helpers import generate_user_id, sanitize_text
from app.utils.validators import validate_user_id, ValidationResult


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=Dict[str, str])
async def create_user(
    username: Optional[str] = None,
    email: Optional[str] = None,
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, str]:
    """
    Create a new user account.
    
    Args:
        username: Optional username
        email: Optional email address
        chat_service: Chat service dependency
    
    Returns:
        User creation response with user ID
    """
    try:
        # Generate user ID
        user_id = generate_user_id()
        
        # Sanitize inputs
        if username:
            username = sanitize_text(username, max_length=50)
        if email:
            email = sanitize_text(email, max_length=100)
        
        # In a real application, store user data in database
        # For now, just return the generated user ID
        
        logger.info(f"Created new user: {user_id}")
        
        return {
            "user_id": user_id,
            "username": username or f"user_{user_id[:8]}",
            "email": email or "",
            "created_at": datetime.utcnow().isoformat(),
            "message": "User created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/{user_id}/profile", response_model=Dict[str, Any])
async def get_user_profile(
    user_id: str,
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, Any]:
    """
    Get user profile information.
    
    Args:
        user_id: User identifier
        chat_service: Chat service dependency
    
    Returns:
        User profile data
    """
    try:
        # Validate user ID
        validation = validate_user_id(user_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {', '.join(validation.errors)}")
        
        # Get user conversations
        conversations = await chat_service.get_user_conversations(user_id, limit=100)
        
        # Calculate user statistics
        total_conversations = len(conversations)
        total_messages = sum(conv.message_count for conv in conversations)
        
        # Get most recent conversation
        most_recent = conversations[0] if conversations else None
        
        profile = {
            "user_id": user_id,
            "statistics": {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "most_recent_activity": most_recent.updated_at.isoformat() if most_recent else None,
                "account_created": "2023-10-09T00:00:00Z"  # Placeholder
            },
            "recent_conversations": conversations[:5],  # Last 5 conversations
            "preferences": {
                "default_model": "gpt-3.5-turbo",
                "default_temperature": 0.7,
                "default_max_tokens": 1000
            }
        }
        
        logger.info(f"Retrieved profile for user: {user_id}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")


@router.get("/{user_id}/conversations", response_model=List[ConversationResponse])
async def get_user_conversations_detailed(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of conversations to return"),
    offset: int = Query(0, ge=0, description="Number of conversations to skip"),
    include_archived: bool = Query(False, description="Include archived conversations"),
    sort_by: str = Query("updated_at", description="Sort field (updated_at, created_at, message_count)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    chat_service: ChatService = Depends(ChatService)
) -> List[ConversationResponse]:
    """
    Get detailed conversation list for a user with filtering and sorting.
    
    Args:
        user_id: User identifier
        limit: Maximum number of conversations
        offset: Number of conversations to skip
        include_archived: Whether to include archived conversations
        sort_by: Field to sort by
        sort_order: Sort order
        chat_service: Chat service dependency
    
    Returns:
        List of user conversations
    """
    try:
        # Validate user ID
        validation = validate_user_id(user_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {', '.join(validation.errors)}")
        
        # Get conversations
        conversations = await chat_service.get_user_conversations(user_id, limit=limit, offset=offset)
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
        return conversations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")


@router.delete("/{user_id}", response_model=Dict[str, str])
async def delete_user(
    user_id: str,
    confirm: bool = Query(False, description="Confirmation required for deletion"),
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, str]:
    """
    Delete a user account and all associated data.
    
    Args:
        user_id: User identifier
        confirm: Confirmation flag
        chat_service: Chat service dependency
    
    Returns:
        Deletion confirmation
    """
    try:
        if not confirm:
            raise HTTPException(
                status_code=400, 
                detail="User deletion requires confirmation. Add ?confirm=true to the request."
            )
        
        # Validate user ID
        validation = validate_user_id(user_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {', '.join(validation.errors)}")
        
        # Get all user conversations
        conversations = await chat_service.get_user_conversations(user_id, limit=1000)
        
        # Delete all conversations
        for conversation in conversations:
            await chat_service.delete_conversation(conversation.conversation_id)
        
        # In a real application, also delete user record from database
        
        logger.info(f"Deleted user {user_id} and {len(conversations)} conversations")
        
        return {
            "message": f"User {user_id} and all associated data deleted successfully",
            "conversations_deleted": len(conversations),
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@router.put("/{user_id}/preferences", response_model=Dict[str, Any])
async def update_user_preferences(
    user_id: str,
    preferences: Dict[str, Any],
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, Any]:
    """
    Update user preferences.
    
    Args:
        user_id: User identifier
        preferences: User preferences to update
        chat_service: Chat service dependency
    
    Returns:
        Updated preferences
    """
    try:
        # Validate user ID
        validation = validate_user_id(user_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {', '.join(validation.errors)}")
        
        # Validate preferences
        allowed_preferences = {
            "default_model", "default_temperature", "default_max_tokens",
            "theme", "language", "notifications_enabled"
        }
        
        filtered_preferences = {
            key: value for key, value in preferences.items()
            if key in allowed_preferences
        }
        
        # In a real application, save to database
        logger.info(f"Updated preferences for user {user_id}")
        
        return {
            "user_id": user_id,
            "preferences": filtered_preferences,
            "updated_at": datetime.utcnow().isoformat(),
            "message": "Preferences updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")


@router.get("/{user_id}/analytics", response_model=Dict[str, Any])
async def get_user_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, Any]:
    """
    Get user activity analytics.
    
    Args:
        user_id: User identifier
        days: Number of days to analyze
        chat_service: Chat service dependency
    
    Returns:
        User analytics data
    """
    try:
        # Validate user ID
        validation = validate_user_id(user_id)
        if not validation.is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid user ID: {', '.join(validation.errors)}")
        
        # Get user conversations
        conversations = await chat_service.get_user_conversations(user_id, limit=1000)
        
        # Calculate analytics
        total_conversations = len(conversations)
        total_messages = sum(conv.message_count for conv in conversations)
        avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
        
        # Recent activity (last 7 days)
        recent_conversations = [
            conv for conv in conversations
            if (datetime.utcnow() - conv.updated_at).days <= 7
        ]
        
        analytics = {
            "user_id": user_id,
            "period_days": days,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "average_messages_per_conversation": round(avg_messages_per_conversation, 2),
            "recent_activity": {
                "conversations_last_7_days": len(recent_conversations),
                "messages_last_7_days": sum(conv.message_count for conv in recent_conversations)
            },
            "most_active_day": None,  # Placeholder - would need detailed message timestamps
            "preferred_models": ["gpt-3.5-turbo"],  # Placeholder
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated analytics for user {user_id}")
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")