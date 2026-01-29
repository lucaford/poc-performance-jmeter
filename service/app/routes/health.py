from datetime import datetime
from fastapi import APIRouter
from app.models.schemas import HealthResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint - retorna status OK inmediatamente sin delay
    """
    logger.info("Health check requested")
    return HealthResponse(
        status="OK",
        timestamp=datetime.utcnow()
    )

