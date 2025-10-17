"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from app.services.health_service import HealthService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=Dict[str, Any])
async def health_check(
    health_service: HealthService = Depends(HealthService)
) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns:
        Dict containing system health status
    """
    try:
        health_status = await health_service.get_health_status()
        logger.info("Health check performed successfully")
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/liveness")
async def liveness_probe() -> Dict[str, str]:
    """
    Simple liveness probe for container orchestration.
    
    Returns:
        Basic alive status
    """
    return {"status": "alive"}


@router.get("/readiness")
async def readiness_probe(
    health_service: HealthService = Depends(HealthService)
) -> Dict[str, Any]:
    """
    Readiness probe to check if application is ready to serve traffic.
    
    Returns:
        Readiness status with dependencies check
    """
    try:
        readiness_status = await health_service.check_readiness()
        return readiness_status
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "error": str(e)
        }