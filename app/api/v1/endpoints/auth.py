"""
Authentication endpoints for user login, registration, and token management.
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Dict, Any
from pydantic import BaseModel, Field
import logging
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.utils.auth import auth_service, get_current_user, AuthenticationError


router = APIRouter()
logger = logging.getLogger(__name__)


class UserRegistration(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str = Field(None, max_length=100, description="Full name")


class UserLogin(BaseModel):
    """User login request model."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_info: Dict[str, Any] = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="Refresh token")


@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration) -> TokenResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
    
    Returns:
        Authentication tokens and user information
    """
    try:
        # In a real application, check if user already exists
        # For now, simulate user creation
        
        # Hash the password
        hashed_password = auth_service.hash_password(user_data.password)
        
        # Create user record (mock)
        user_id = f"user_{hash(user_data.username) % 100000}"
        user_record = {
            "user_id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "is_admin": False,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Create tokens
        token_data = {
            "sub": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "is_admin": False
        }
        
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token({"sub": user_id})
        
        logger.info(f"New user registered: {user_data.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user_info={
                "user_id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "is_admin": False
            }
        )
        
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin) -> TokenResponse:
    """
    Authenticate user and return tokens.
    
    Args:
        user_credentials: User login credentials
    
    Returns:
        Authentication tokens and user information
    """
    try:
        # In a real application, query the database for user
        # For now, simulate user lookup and authentication
        
        # Mock user data (in production, fetch from database)
        if user_credentials.username == "admin":
            user_record = {
                "user_id": "admin_001",
                "username": "admin",
                "email": "admin@chatbot.com",
                "full_name": "System Administrator",
                "hashed_password": auth_service.hash_password("admin123"),
                "is_admin": True,
                "is_active": True
            }
        else:
            # Mock regular user
            user_record = {
                "user_id": f"user_{hash(user_credentials.username) % 100000}",
                "username": user_credentials.username,
                "email": f"{user_credentials.username}@example.com",
                "full_name": user_credentials.username.title(),
                "hashed_password": auth_service.hash_password("password123"),
                "is_admin": False,
                "is_active": True
            }
        
        # Verify password
        if not auth_service.verify_password(user_credentials.password, user_record["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if user is active
        if not user_record.get("is_active", True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create tokens
        token_data = {
            "sub": user_record["user_id"],
            "username": user_record["username"],
            "email": user_record["email"],
            "is_admin": user_record["is_admin"]
        }
        
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token({"sub": user_record["user_id"]})
        
        logger.info(f"User logged in: {user_credentials.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user_info={
                "user_id": user_record["user_id"],
                "username": user_record["username"],
                "email": user_record["email"],
                "full_name": user_record["full_name"],
                "is_admin": user_record["is_admin"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_request: Refresh token request
    
    Returns:
        New authentication tokens
    """
    try:
        # Verify refresh token
        payload = auth_service.verify_token(refresh_request.refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        # In a real application, fetch user data from database
        # For now, simulate user lookup
        if user_id == "admin_001":
            user_record = {
                "user_id": "admin_001",
                "username": "admin",
                "email": "admin@chatbot.com",
                "full_name": "System Administrator",
                "is_admin": True,
                "is_active": True
            }
        else:
            user_record = {
                "user_id": user_id,
                "username": f"user_{user_id[-3:]}",
                "email": f"user_{user_id[-3:]}@example.com",
                "full_name": f"User {user_id[-3:]}",
                "is_admin": False,
                "is_active": True
            }
        
        # Create new tokens
        token_data = {
            "sub": user_record["user_id"],
            "username": user_record["username"],
            "email": user_record["email"],
            "is_admin": user_record["is_admin"]
        }
        
        access_token = auth_service.create_access_token(token_data)
        new_refresh_token = auth_service.create_refresh_token({"sub": user_record["user_id"]})
        
        logger.info(f"Token refreshed for user: {user_record['username']}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=auth_service.access_token_expire_minutes * 60,
            user_info={
                "user_id": user_record["user_id"],
                "username": user_record["username"],
                "email": user_record["email"],
                "full_name": user_record["full_name"],
                "is_admin": user_record["is_admin"]
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")


@router.post("/logout", response_model=Dict[str, str])
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Logout user and invalidate tokens.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Logout confirmation
    """
    try:
        # In a real application, add tokens to blacklist
        # For now, just log the logout
        
        logger.info(f"User logged out: {current_user['username']}")
        
        return {
            "message": "Successfully logged out",
            "user_id": current_user["user_id"],
            "logged_out_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user information
    """
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "is_admin": current_user["is_admin"],
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.post("/generate-api-key", response_model=Dict[str, str])
async def generate_user_api_key(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Generate a new API key for the current user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Generated API key
    """
    try:
        api_key = auth_service.generate_api_key(current_user["user_id"])
        
        logger.info(f"API key generated for user: {current_user['username']}")
        
        return {
            "api_key": api_key,
            "user_id": current_user["user_id"],
            "generated_at": datetime.utcnow().isoformat(),
            "note": "Store this API key securely. It will not be shown again."
        }
        
    except Exception as e:
        logger.error(f"API key generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate API key")


@router.post("/change-password", response_model=Dict[str, str])
async def change_user_password(
    current_password: str = Form(...),
    new_password: str = Form(..., min_length=8),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Change user password.
    
    Args:
        current_password: Current password
        new_password: New password
        current_user: Current authenticated user
    
    Returns:
        Password change confirmation
    """
    try:
        # In a real application, verify current password against database
        # For now, simulate password verification
        
        # Hash new password
        new_hashed_password = auth_service.hash_password(new_password)
        
        # In production, update the password in the database
        
        logger.info(f"Password changed for user: {current_user['username']}")
        
        return {
            "message": "Password changed successfully",
            "user_id": current_user["user_id"],
            "changed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to change password")