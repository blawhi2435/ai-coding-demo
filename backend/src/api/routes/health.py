"""
Health check endpoint for system monitoring

Provides health status for all critical services (MongoDB, LLM).
"""

from datetime import datetime
from typing import Dict
from fastapi import APIRouter, Response, status
import httpx

from src.db.mongo import check_mongo_health
from src.config import settings
from src.utils.logger import logger

router = APIRouter()


async def check_llm_health() -> bool:
    """
    Check if the LLM service is healthy.

    Returns:
        bool: True if LLM service is accessible, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.LLM_SERVICE_URL}/api/tags")
            return response.status_code == 200
    except Exception as e:
        logger.warning(
            f"LLM health check failed",
            extra={"error": str(e), "llm_url": settings.LLM_SERVICE_URL},
        )
        return False


def determine_overall_status(service_statuses: Dict[str, str]) -> str:
    """
    Determine the overall system health status based on individual service statuses.

    Args:
        service_statuses: Dictionary of service names to their status ('up' or 'down')

    Returns:
        str: 'healthy' if all services are up, 'degraded' if some are down, 'unhealthy' if all are down
    """
    up_count = sum(1 for status in service_statuses.values() if status == "up")
    total_count = len(service_statuses)

    if up_count == total_count:
        return "healthy"
    elif up_count == 0:
        return "unhealthy"
    else:
        return "degraded"


@router.get("/health")
async def health_check(response: Response) -> Dict:
    """
    Health check endpoint that verifies connectivity to all critical services.

    Returns:
        Dict: Health status including:
            - status: Overall system health ('healthy', 'degraded', 'unhealthy')
            - services: Individual service health statuses
            - timestamp: ISO 8601 timestamp of the health check

    Status Codes:
        - 200: System is healthy (all services operational)
        - 503: System is degraded or unhealthy (one or more services down)
    """
    logger.info("Health check requested")

    # Check all service health in parallel
    mongodb_healthy = await check_mongo_health()
    llm_healthy = await check_llm_health()

    # Build service status dictionary
    service_statuses = {
        "mongodb": "up" if mongodb_healthy else "down",
        "llm": "up" if llm_healthy else "down",
    }

    # Determine overall status
    overall_status = determine_overall_status(service_statuses)

    # Set appropriate HTTP status code
    if overall_status == "healthy":
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Build response
    health_response = {
        "status": overall_status,
        "services": service_statuses,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Log the health check result
    logger.info(
        f"Health check complete: {overall_status}",
        extra={
            "status": overall_status,
            "services": service_statuses,
        },
    )

    return health_response
