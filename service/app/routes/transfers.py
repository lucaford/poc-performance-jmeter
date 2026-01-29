import random
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import TransferRequest, TransferResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transfers", tags=["transfers"])

# Almacenamiento en memoria de transferencias
TRANSFERS = {}


def simulate_latency(min_ms: int, max_ms: int):
    """Simula latencia aleatoria entre min_ms y max_ms milisegundos"""
    import asyncio
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    return asyncio.sleep(delay)


def simulate_error():
    """Simula un error 500 con probabilidad del 1%"""
    return random.random() < 0.01


@router.post("", response_model=TransferResponse, status_code=201)
async def create_transfer(transfer: TransferRequest, request: Request):
    """
    Crea una nueva transferencia
    - Delay aleatorio: 50-200ms
    - 1% probabilidad de error 500
    - Valida que el monto sea positivo (ya validado por Pydantic)
    - Valida que las cuentas existan (1-100)
    """
    request_id = str(uuid.uuid4())
    logger.info(
        f"Request ID: {request_id} - POST /api/transfers - "
        f"From: {transfer.from_account}, To: {transfer.to_account}, Amount: {transfer.amount}"
    )
    
    # Simular error ocasional
    if simulate_error():
        logger.error(f"Request ID: {request_id} - Simulated 500 error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error (simulated)"
        )
    
    # Validar que las cuentas existan (rango 1-100)
    from app.routes.accounts import ACCOUNTS
    if transfer.from_account not in ACCOUNTS:
        logger.warning(f"Request ID: {request_id} - From account {transfer.from_account} not found")
        raise HTTPException(
            status_code=404,
            detail=f"From account {transfer.from_account} not found"
        )
    
    if transfer.to_account not in ACCOUNTS:
        logger.warning(f"Request ID: {request_id} - To account {transfer.to_account} not found")
        raise HTTPException(
            status_code=404,
            detail=f"To account {transfer.to_account} not found"
        )
    
    # Validar que el monto sea positivo (ya validado por Pydantic, pero por seguridad)
    if transfer.amount <= 0:
        logger.warning(f"Request ID: {request_id} - Invalid amount: {transfer.amount}")
        raise HTTPException(
            status_code=400,
            detail="Amount must be positive"
        )
    
    # Simular latencia de operación (50-200ms)
    await simulate_latency(50, 200)
    
    # Crear la transferencia
    transfer_id = str(uuid.uuid4())
    status = "completed" if not simulate_error() else "failed"
    
    transfer_data = {
        "transfer_id": transfer_id,
        "from_account": transfer.from_account,
        "to_account": transfer.to_account,
        "amount": transfer.amount,
        "status": status,
        "timestamp": datetime.utcnow(),
        "description": transfer.description
    }
    
    TRANSFERS[transfer_id] = transfer_data
    
    logger.info(
        f"Request ID: {request_id} - Transfer {transfer_id} created with status {status}"
    )
    
    return TransferResponse(**transfer_data)


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(transfer_id: str, request: Request):
    """
    Consulta el estado de una transferencia
    - Delay aleatorio: 20-80ms
    - 1% probabilidad de error 500
    - 404 si transfer_id no existe
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - GET /api/transfers/{transfer_id}")
    
    # Simular error ocasional
    if simulate_error():
        logger.error(f"Request ID: {request_id} - Simulated 500 error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error (simulated)"
        )
    
    # Simular latencia de consulta (20-80ms)
    await simulate_latency(20, 80)
    
    if transfer_id not in TRANSFERS:
        logger.warning(f"Request ID: {request_id} - Transfer {transfer_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Transfer {transfer_id} not found"
        )
    
    transfer = TRANSFERS[transfer_id]
    logger.info(f"Request ID: {request_id} - Transfer {transfer_id} retrieved")
    
    return TransferResponse(**transfer)

