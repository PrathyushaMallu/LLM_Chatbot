"""
Gemini API registration and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.utils.auth import get_current_user, get_current_admin_user
from app.services.enhanced_llm_service import enhanced_llm_service, LLMProvider
from config.settings import settings


router = APIRouter()
logger = logging.getLogger(__name__)


class GeminiRegistration(BaseModel):
    """Gemini API registration model."""
    api_key: str = Field(..., min_length=10, description="Google Gemini API key")
    project_id: str = Field(None, description="Google Cloud Project ID (optional)")
    default_model: str = Field("gemini-pro", description="Default Gemini model")
    description: str = Field(None, max_length=200, description="Registration description")


class LLMProviderConfig(BaseModel):
    """LLM provider configuration model."""
    provider: str = Field(..., description="Provider name (openai/gemini)")
    model: str = Field(..., description="Model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature setting")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum tokens")
    is_default: bool = Field(False, description="Set as default provider")


class TestMessage(BaseModel):
    """Test message model."""
    message: str = Field(..., min_length=1, max_length=500, description="Test message")
    provider: str = Field("gemini", description="Provider to test (openai/gemini)")
    model: str = Field(None, description="Specific model to test")


@router.post("/register", response_model=Dict[str, Any])
async def register_gemini_api(
    gemini_data: GeminiRegistration,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Register Gemini API key for the system.
    
    Args:
        gemini_data: Gemini registration data
        current_user: Current admin user
    
    Returns:
        Registration confirmation and status
    """
    try:
        # Validate API key format (basic validation)
        if not gemini_data.api_key.startswith(('AIza', 'ya29')):
            raise HTTPException(
                status_code=400,
                detail="Invalid Gemini API key format. Key should start with 'AIza' or 'ya29'"
            )
        
        # Test the API key
        from app.services.enhanced_llm_service import GeminiService
        test_service = GeminiService(gemini_data.api_key)
        
        # Try a simple test
        test_messages = [{"role": "user", "content": "Hello, please respond with 'API key is working'"}]
        
        try:
            test_result = await test_service.generate_response(
                messages=test_messages,
                model=gemini_data.default_model,
                max_tokens=50
            )
            
            # If we get here, the API key works
            api_key_status = "valid"
            test_response = test_result.get("response", "Test successful")
            
        except Exception as e:
            api_key_status = "invalid"
            test_response = str(e)
            
            if "API key" in str(e).lower() or "authentication" in str(e).lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid Gemini API key: {str(e)}"
                )
        
        # In a real application, store the API key securely in database
        # For now, we'll simulate registration
        registration_record = {
            "user_id": current_user["user_id"],
            "api_key_hash": f"gemini_key_{hash(gemini_data.api_key) % 10000}",
            "project_id": gemini_data.project_id,
            "default_model": gemini_data.default_model,
            "description": gemini_data.description,
            "status": api_key_status,
            "registered_at": datetime.utcnow().isoformat(),
            "last_tested": datetime.utcnow().isoformat(),
            "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
        }
        
        logger.info(f"Gemini API registered by admin: {current_user['username']}")
        
        return {
            "message": "Gemini API key registered successfully",
            "registration_id": f"gemini_reg_{hash(gemini_data.api_key) % 100000}",
            "status": api_key_status,
            "default_model": gemini_data.default_model,
            "available_models": [
                "gemini-pro",
                "gemini-pro-vision"
            ],
            "test_result": test_response,
            "registered_at": registration_record["registered_at"],
            "next_steps": [
                "Set Gemini as default provider in system settings",
                "Configure model preferences",
                "Test with chat endpoints"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini API registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/providers", response_model=Dict[str, Any])
async def get_available_providers(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of available LLM providers and their status.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Available providers and their configurations
    """
    try:
        providers_info = {
            "available_providers": enhanced_llm_service.get_available_providers(),
            "default_provider": settings.default_llm_provider,
            "provider_details": {
                "openai": {
                    "name": "OpenAI",
                    "models": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
                    "status": "configured" if settings.openai_api_key else "not_configured",
                    "default_model": settings.openai_model,
                    "features": ["chat", "completion", "streaming"]
                },
                "gemini": {
                    "name": "Google Gemini",
                    "models": ["gemini-pro", "gemini-pro-vision"],
                    "status": "configured" if settings.gemini_api_key else "not_configured",
                    "default_model": settings.gemini_model,
                    "features": ["chat", "completion", "vision"]
                }
            },
            "current_settings": {
                "temperature": settings.temperature,
                "max_tokens": settings.max_tokens
            }
        }
        
        return providers_info
        
    except Exception as e:
        logger.error(f"Error getting providers info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get providers info: {str(e)}")


@router.post("/test", response_model=Dict[str, Any])
async def test_provider(
    test_data: TestMessage,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Test a specific LLM provider with a message.
    
    Args:
        test_data: Test message and provider information
        current_user: Current authenticated user
    
    Returns:
        Test response and performance metrics
    """
    try:
        # Validate provider
        if test_data.provider not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider. Must be 'openai' or 'gemini'"
            )
        
        provider = LLMProvider(test_data.provider)
        
        # Prepare test message
        messages = [{"role": "user", "content": test_data.message}]
        
        # Generate response
        start_time = datetime.utcnow()
        
        result = await enhanced_llm_service.generate_response(
            messages=messages,
            provider=provider
        )
        
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        
        logger.info(f"User {current_user['username']} tested {test_data.provider} provider")
        
        return {
            "test_message": test_data.message,
            "provider": test_data.provider,
            "model": result.get("model"),
            "response": result.get("response"),
            "performance": {
                "response_time_seconds": total_time,
                "tokens_used": result.get("tokens_used"),
                "finish_reason": result.get("finish_reason")
            },
            "test_metadata": {
                "user_id": current_user["user_id"],
                "tested_at": start_time.isoformat(),
                "provider_status": "working"
            }
        }
        
    except Exception as e:
        logger.error(f"Provider test failed: {str(e)}")
        return {
            "test_message": test_data.message,
            "provider": test_data.provider,
            "response": None,
            "error": str(e),
            "performance": {
                "response_time_seconds": 0,
                "tokens_used": 0,
                "finish_reason": "error"
            },
            "test_metadata": {
                "user_id": current_user["user_id"],
                "tested_at": datetime.utcnow().isoformat(),
                "provider_status": "failed"
            }
        }


@router.post("/configure", response_model=Dict[str, Any])
async def configure_provider(
    config_data: LLMProviderConfig,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """
    Configure LLM provider settings.
    
    Args:
        config_data: Provider configuration data
        current_user: Current admin user
    
    Returns:
        Configuration update confirmation
    """
    try:
        # Validate provider
        if config_data.provider not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider. Must be 'openai' or 'gemini'"
            )
        
        # Validate model for provider
        if config_data.provider == "openai":
            valid_models = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        else:  # gemini
            valid_models = ["gemini-pro", "gemini-pro-vision"]
        
        if config_data.model not in valid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model for {config_data.provider}. Valid models: {valid_models}"
            )
        
        # In a real application, update the configuration in database/settings
        # For now, simulate configuration update
        
        configuration = {
            "provider": config_data.provider,
            "model": config_data.model,
            "temperature": config_data.temperature,
            "max_tokens": config_data.max_tokens,
            "is_default": config_data.is_default,
            "configured_by": current_user["user_id"],
            "configured_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Provider {config_data.provider} configured by admin: {current_user['username']}")
        
        return {
            "message": f"{config_data.provider.title()} provider configured successfully",
            "configuration": configuration,
            "previous_default": settings.default_llm_provider,
            "new_default": config_data.provider if config_data.is_default else settings.default_llm_provider,
            "restart_required": config_data.is_default  # Would require restart to change default provider
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def check_providers_health(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check health status of all configured LLM providers.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Health status of all providers
    """
    try:
        health_results = {}
        
        # Test each available provider
        for provider_name in enhanced_llm_service.get_available_providers():
            provider = LLMProvider(provider_name)
            health_result = await enhanced_llm_service.test_provider_connection(provider)
            health_results[provider_name] = health_result
        
        # Overall system health
        all_healthy = all(
            result.get("status") == "healthy" 
            for result in health_results.values()
        )
        
        return {
            "overall_status": "healthy" if all_healthy else "degraded",
            "providers": health_results,
            "default_provider": settings.default_llm_provider,
            "default_provider_healthy": health_results.get(
                settings.default_llm_provider, {}
            ).get("status") == "healthy",
            "checked_at": datetime.utcnow().isoformat(),
            "checked_by": current_user["user_id"]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.delete("/provider/{provider_name}", response_model=Dict[str, str])
async def remove_provider_configuration(
    provider_name: str,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """
    Remove provider configuration (admin only).
    
    Args:
        provider_name: Name of provider to remove
        current_user: Current admin user
    
    Returns:
        Removal confirmation
    """
    try:
        if provider_name not in ["openai", "gemini"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider name"
            )
        
        # In a real application, remove API keys and configuration from database
        # For now, simulate removal
        
        logger.info(f"Provider {provider_name} configuration removed by admin: {current_user['username']}")
        
        return {
            "message": f"{provider_name.title()} provider configuration removed",
            "provider": provider_name,
            "removed_by": current_user["username"],
            "removed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider removal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Provider removal failed: {str(e)}")