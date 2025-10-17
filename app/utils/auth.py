"""
Authentication and security utilities for the API.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
import hashlib
import hmac
from datetime import datetime, timedelta
import logging
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import settings


logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class AuthService:
    """Service for handling authentication and authorization."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Token payload data
        
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Token payload data
        
        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded token payload
        
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using HMAC-SHA256.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return hmac.new(
            self.secret_key.encode(),
            password.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
        
        Returns:
            True if password is valid
        """
        return hmac.compare_digest(
            self.hash_password(plain_password),
            hashed_password
        )
    
    def generate_api_key(self, user_id: str) -> str:
        """
        Generate an API key for a user.
        
        Args:
            user_id: User identifier
        
        Returns:
            Generated API key
        """
        data = f"{user_id}:{datetime.utcnow().isoformat()}"
        api_key = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"chatbot_{api_key[:32]}"
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """
        Verify an API key and return the associated user ID.
        
        Args:
            api_key: API key to verify
        
        Returns:
            User ID if valid, None otherwise
        """
        # In a real application, this would query a database
        # For now, we'll implement a simple verification
        if api_key.startswith("chatbot_") and len(api_key) == 40:
            # Mock user ID extraction
            return f"user_{api_key[-8:]}"
        return None


# Global auth service instance
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP authorization credentials
    
    Returns:
        Current user information
    
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Check if it's a Bearer token (JWT)
        if credentials.scheme.lower() == "bearer":
            payload = auth_service.verify_token(credentials.credentials)
            
            # Verify token type
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            return {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "is_admin": payload.get("is_admin", False)
            }
        
        # Check if it's an API key
        elif credentials.scheme.lower() == "apikey":
            user_id = auth_service.verify_api_key(credentials.credentials)
            if not user_id:
                raise AuthenticationError("Invalid API key")
            
            return {
                "user_id": user_id,
                "username": f"api_user_{user_id}",
                "email": None,
                "is_admin": False
            }
        
        else:
            raise AuthenticationError("Unsupported authentication scheme")
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated admin user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current admin user information
    
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}  # {user_id: [timestamp, ...]}
        self.max_requests_per_minute = 60
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request is allowed based on rate limiting.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if request is allowed
        """
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > minute_ago
            ]
        else:
            self.requests[user_id] = []
        
        # Check if under limit
        if len(self.requests[user_id]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to check rate limiting for the current user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user if rate limit not exceeded
    
    Raises:
        HTTPException: If rate limit exceeded
    """
    user_id = current_user["user_id"]
    
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    return current_user


def require_api_key(api_key: str) -> str:
    """
    Validate an API key from query parameters or headers.
    
    Args:
        api_key: API key to validate
    
    Returns:
        User ID associated with the API key
    
    Raises:
        HTTPException: If API key is invalid
    """
    user_id = auth_service.verify_api_key(api_key)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return user_id