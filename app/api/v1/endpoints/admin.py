"""
Admin endpoints for system management and monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Dict, Any, Optional
import logging
import sys
import os
from datetime import datetime, timedelta
import asyncio

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.health_service import HealthService
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService
from config.settings import settings


router = APIRouter()
logger = logging.getLogger(__name__)


def verify_admin_token(authorization: str = Header(None)) -> bool:
    """
    Verify admin authorization token.
    
    Args:
        authorization: Authorization header
    
    Returns:
        True if authorized
    
    Raises:
        HTTPException: If not authorized
    """
    # In production, implement proper JWT token validation
    if not authorization or authorization != f"Bearer {settings.secret_key}":
        raise HTTPException(
            status_code=401,
            detail="Admin authorization required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return True


@router.get("/system/status", response_model=Dict[str, Any])
async def get_system_status(
    admin_authorized: bool = Depends(verify_admin_token),
    health_service: HealthService = Depends(HealthService)
) -> Dict[str, Any]:
    """
    Get comprehensive system status for administrators.
    
    Args:
        admin_authorized: Admin authorization dependency
        health_service: Health service dependency
    
    Returns:
        Detailed system status
    """
    try:
        # Get health status
        health_status = await health_service.get_health_status()
        
        # Add additional admin-only information
        system_status = {
            **health_status,
            "admin_info": {
                "settings": {
                    "debug_mode": settings.debug,
                    "log_level": settings.log_level,
                    "api_version": settings.api_v1_str,
                    "allowed_origins": settings.allowed_origins
                },
                "environment": {
                    "app_name": settings.app_name,
                    "version": settings.version,
                    "host": settings.host,
                    "port": settings.port
                }
            }
        }
        
        logger.info("Admin accessed system status")
        return system_status
        
    except Exception as e:
        logger.error(f"Error retrieving system status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system status: {str(e)}")


@router.get("/system/metrics", response_model=Dict[str, Any])
async def get_system_metrics(
    admin_authorized: bool = Depends(verify_admin_token),
    hours: int = Query(24, ge=1, le=168, description="Hours of metrics to retrieve"),
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, Any]:
    """
    Get system usage metrics.
    
    Args:
        admin_authorized: Admin authorization dependency
        hours: Number of hours of metrics to retrieve
        chat_service: Chat service dependency
    
    Returns:
        System usage metrics
    """
    try:
        # In a real application, this would query a metrics database
        # For now, provide mock data structure
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        metrics = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "api_metrics": {
                "total_requests": 1250,  # Mock data
                "successful_requests": 1200,
                "failed_requests": 50,
                "average_response_time_ms": 245,
                "requests_per_hour": 52
            },
            "chat_metrics": {
                "total_messages": 890,
                "total_conversations": 156,
                "average_messages_per_conversation": 5.7,
                "unique_users": 89
            },
            "llm_metrics": {
                "total_tokens_used": 45670,
                "average_tokens_per_request": 51,
                "most_used_model": "gpt-3.5-turbo",
                "model_usage": {
                    "gpt-3.5-turbo": 0.85,
                    "gpt-4": 0.15
                }
            },
            "system_metrics": {
                "cpu_usage_avg": 23.5,
                "memory_usage_avg": 456.7,
                "disk_usage_gb": 12.3,
                "network_requests": 2340
            }
        }
        
        logger.info(f"Admin retrieved system metrics for {hours} hours")
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.get("/users/overview", response_model=Dict[str, Any])
async def get_users_overview(
    admin_authorized: bool = Depends(verify_admin_token),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to include"),
    chat_service: ChatService = Depends(ChatService)
) -> Dict[str, Any]:
    """
    Get overview of all users in the system.
    
    Args:
        admin_authorized: Admin authorization dependency
        limit: Maximum number of users to include
        chat_service: Chat service dependency
    
    Returns:
        Users overview data
    """
    try:
        # In a real application, this would query the user database
        # For now, provide mock overview structure
        
        overview = {
            "total_users": 245,  # Mock data
            "active_users_last_24h": 67,
            "new_users_last_7_days": 12,
            "top_users": [
                {
                    "user_id": "user_12345",
                    "total_conversations": 45,
                    "total_messages": 234,
                    "last_active": "2023-10-09T15:30:00Z"
                },
                {
                    "user_id": "user_67890",
                    "total_conversations": 38,
                    "total_messages": 187,
                    "last_active": "2023-10-09T14:22:00Z"
                }
            ],
            "user_activity_distribution": {
                "very_active": 23,  # >20 conversations
                "active": 56,       # 5-20 conversations
                "moderate": 89,     # 1-5 conversations
                "inactive": 77      # 0 conversations
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info("Admin retrieved users overview")
        return overview
        
    except Exception as e:
        logger.error(f"Error retrieving users overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users overview: {str(e)}")


@router.post("/system/maintenance", response_model=Dict[str, str])
async def trigger_maintenance_task(
    task: str = Query(..., description="Maintenance task to execute"),
    admin_authorized: bool = Depends(verify_admin_token)
) -> Dict[str, str]:
    """
    Trigger system maintenance tasks.
    
    Args:
        task: Maintenance task to execute
        admin_authorized: Admin authorization dependency
    
    Returns:
        Task execution result
    """
    try:
        valid_tasks = [
            "cleanup_logs",
            "cleanup_temp_files", 
            "refresh_cache",
            "health_check",
            "backup_conversations"
        ]
        
        if task not in valid_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task. Valid tasks: {', '.join(valid_tasks)}"
            )
        
        # Execute maintenance task
        result = await execute_maintenance_task(task)
        
        logger.info(f"Admin executed maintenance task: {task}")
        
        return {
            "task": task,
            "status": "completed",
            "message": result,
            "executed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing maintenance task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")


async def execute_maintenance_task(task: str) -> str:
    """
    Execute a specific maintenance task.
    
    Args:
        task: Task to execute
    
    Returns:
        Task result message
    """
    if task == "cleanup_logs":
        # Simulate log cleanup
        await asyncio.sleep(1)
        return "Log files cleaned up successfully"
    
    elif task == "cleanup_temp_files":
        # Simulate temp file cleanup
        await asyncio.sleep(0.5)
        return "Temporary files cleaned up successfully"
    
    elif task == "refresh_cache":
        # Simulate cache refresh
        await asyncio.sleep(0.3)
        return "Cache refreshed successfully"
    
    elif task == "health_check":
        # Run health check
        health_service = HealthService()
        health_status = await health_service.get_health_status()
        return f"Health check completed. Status: {health_status['status']}"
    
    elif task == "backup_conversations":
        # Simulate conversation backup
        await asyncio.sleep(2)
        return "Conversation backup completed successfully"
    
    else:
        return "Unknown task"


@router.get("/logs", response_model=Dict[str, Any])
async def get_system_logs(
    admin_authorized: bool = Depends(verify_admin_token),
    level: str = Query("INFO", description="Log level filter"),
    lines: int = Query(100, ge=1, le=1000, description="Number of log lines"),
    service: Optional[str] = Query(None, description="Service name filter")
) -> Dict[str, Any]:
    """
    Get system logs for debugging and monitoring.
    
    Args:
        admin_authorized: Admin authorization dependency
        level: Log level to filter by
        lines: Number of log lines to return
        service: Optional service name filter
    
    Returns:
        System logs data
    """
    try:
        # In a real application, read from actual log files
        # For now, provide mock log structure
        
        mock_logs = [
            {
                "timestamp": "2023-10-09T15:30:25.123Z",
                "level": "INFO",
                "service": "chat_service",
                "message": "Message processed successfully for conversation conv_abc123"
            },
            {
                "timestamp": "2023-10-09T15:30:20.456Z",
                "level": "INFO",
                "service": "llm_service",
                "message": "LLM response generated in 1.2 seconds"
            },
            {
                "timestamp": "2023-10-09T15:29:45.789Z",
                "level": "WARNING",
                "service": "health_service",
                "message": "Memory usage approaching threshold: 85%"
            }
        ]
        
        # Filter logs if service specified
        if service:
            mock_logs = [log for log in mock_logs if log["service"] == service]
        
        # Filter by log level
        level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
        min_priority = level_priority.get(level.upper(), 1)
        mock_logs = [
            log for log in mock_logs 
            if level_priority.get(log["level"], 1) >= min_priority
        ]
        
        # Limit number of lines
        mock_logs = mock_logs[:lines]
        
        logs_data = {
            "logs": mock_logs,
            "total_lines": len(mock_logs),
            "filters": {
                "level": level,
                "service": service,
                "lines": lines
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Admin retrieved {len(mock_logs)} log lines")
        return logs_data
        
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")


@router.put("/system/config", response_model=Dict[str, Any])
async def update_system_config(
    config_updates: Dict[str, Any],
    admin_authorized: bool = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Update system configuration (runtime settings).
    
    Args:
        config_updates: Configuration updates to apply
        admin_authorized: Admin authorization dependency
    
    Returns:
        Updated configuration status
    """
    try:
        # Define updatable settings
        updatable_settings = {
            "log_level": ["DEBUG", "INFO", "WARNING", "ERROR"],
            "rate_limit_per_minute": range(1, 1001),
            "max_tokens": range(1, 4001),
            "temperature": "float"
        }
        
        applied_updates = {}
        skipped_updates = {}
        
        for key, value in config_updates.items():
            if key in updatable_settings:
                # Validate the value
                valid_values = updatable_settings[key]
                
                if isinstance(valid_values, list) and value in valid_values:
                    applied_updates[key] = value
                elif isinstance(valid_values, range) and value in valid_values:
                    applied_updates[key] = value
                elif valid_values == "float" and isinstance(value, (int, float)):
                    applied_updates[key] = float(value)
                else:
                    skipped_updates[key] = f"Invalid value: {value}"
            else:
                skipped_updates[key] = "Setting not updatable at runtime"
        
        # In a real application, apply the configuration changes
        
        logger.info(f"Admin updated system configuration: {applied_updates}")
        
        return {
            "applied_updates": applied_updates,
            "skipped_updates": skipped_updates,
            "updated_at": datetime.utcnow().isoformat(),
            "restart_required": False
        }
        
    except Exception as e:
        logger.error(f"Error updating system config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")