"""
Health service for system health checks and monitoring.
"""

import asyncio
import logging
import time
import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import settings
from app.services.llm_service import LLMService


class HealthService:
    """Service for health checks and system monitoring."""
    
    def __init__(self):
        """Initialize health service."""
        self.logger = logging.getLogger(__name__)
        self.llm_service = LLMService()
        self.startup_time = datetime.utcnow()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Dictionary containing system health information
        """
        start_time = time.time()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.startup_time).total_seconds(),
            "version": settings.version,
            "app_name": settings.app_name,
            "checks": {}
        }
        
        try:
            # Check LLM service
            llm_healthy = await self._check_llm_service()
            health_status["checks"]["llm_service"] = {
                "status": "healthy" if llm_healthy else "unhealthy",
                "details": "OpenAI API connection" if llm_healthy else "OpenAI API unavailable"
            }
            
            # Check database connectivity (placeholder)
            db_healthy = await self._check_database()
            health_status["checks"]["database"] = {
                "status": "healthy" if db_healthy else "unhealthy",
                "details": "Database connection OK" if db_healthy else "Database connection failed"
            }
            
            # Check memory usage (basic check)
            memory_status = await self._check_memory()
            health_status["checks"]["memory"] = memory_status
            
            # Check configuration
            config_status = await self._check_configuration()
            health_status["checks"]["configuration"] = config_status
            
            # Determine overall status
            all_checks_healthy = all(
                check["status"] == "healthy" 
                for check in health_status["checks"].values()
            )
            
            if not all_checks_healthy:
                health_status["status"] = "degraded"
            
            health_status["response_time_ms"] = (time.time() - start_time) * 1000
            
        except Exception as e:
            self.logger.error(f"Error during health check: {str(e)}")
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
        
        return health_status
    
    async def check_readiness(self) -> Dict[str, Any]:
        """
        Check if the application is ready to serve requests.
        
        Returns:
            Dictionary containing readiness status
        """
        readiness_checks = []
        
        try:
            # Check critical dependencies
            llm_ready = await self._check_llm_service()
            readiness_checks.append({
                "name": "llm_service",
                "ready": llm_ready,
                "message": "LLM service available" if llm_ready else "LLM service unavailable"
            })
            
            # Check configuration
            config_check = await self._check_configuration()
            config_ready = config_check["status"] == "healthy"
            readiness_checks.append({
                "name": "configuration",
                "ready": config_ready,
                "message": config_check["details"]
            })
            
            # Determine overall readiness
            all_ready = all(check["ready"] for check in readiness_checks)
            
            return {
                "status": "ready" if all_ready else "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": readiness_checks
            }
            
        except Exception as e:
            self.logger.error(f"Error during readiness check: {str(e)}")
            return {
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _check_llm_service(self) -> bool:
        """Check LLM service health."""
        try:
            if not settings.openai_api_key:
                return False
            
            # For demonstration, we'll just check if API key is configured
            # In production, you might want to make a test API call
            return await self.llm_service.validate_api_connection()
            
        except Exception as e:
            self.logger.error(f"LLM service check failed: {str(e)}")
            return False
    
    async def _check_database(self) -> bool:
        """Check database connectivity."""
        try:
            # Placeholder for database health check
            # In production, implement actual database connection test
            return True
            
        except Exception as e:
            self.logger.error(f"Database check failed: {str(e)}")
            return False
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                "status": "healthy" if memory.percent < 90 else "warning",
                "details": f"Memory usage: {memory.percent:.1f}%",
                "used_gb": round(memory.used / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2)
            }
            
        except ImportError:
            return {
                "status": "unknown",
                "details": "psutil not available for memory monitoring"
            }
        except Exception as e:
            return {
                "status": "error",
                "details": f"Memory check failed: {str(e)}"
            }
    
    async def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity."""
        try:
            issues = []
            
            # Check critical settings
            if not settings.openai_api_key:
                issues.append("OpenAI API key not configured")
            
            if not settings.secret_key or settings.secret_key == "your-secret-key-change-in-production":
                issues.append("Secret key not properly configured")
            
            if settings.debug and settings.host != "localhost":
                issues.append("Debug mode enabled in production")
            
            if issues:
                return {
                    "status": "warning",
                    "details": f"Configuration issues: {', '.join(issues)}"
                }
            else:
                return {
                    "status": "healthy",
                    "details": "Configuration OK"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "details": f"Configuration check failed: {str(e)}"
            }