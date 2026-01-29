import random
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import AccountResponse, BalanceResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/accounts", tags=["accounts"])

# Simular datos en memoria: 100 cuentas pre-generadas
ACCOUNTS = {}
for i in range(1, 101):
    ACCOUNTS[str(i)] = {
        "account_id": str(i),
        "holder_name": f"Titular {i}",
        "balance": random.uniform(1000, 100000),
        "currency": "ARS",
        "status": "active"
    }


def simulate_latency(min_ms: int, max_ms: int):
    """Simula latencia aleatoria entre min_ms y max_ms milisegundos"""
    import asyncio
    delay = random.uniform(min_ms / 1000, max_ms / 1000)
    return asyncio.sleep(delay)


def simulate_error():
    """Simula un error 500 con probabilidad del 1%"""
    return random.random() < 0.01


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, request: Request):
    """
    Consulta información de una cuenta
    - Delay aleatorio: 20-80ms
    - 1% probabilidad de error 500
    - 404 si account_id no existe (fuera del rango 1-100)
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - GET /api/accounts/{account_id}")
    
    # Simular error ocasional
    if simulate_error():
        logger.error(f"Request ID: {request_id} - Simulated 500 error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error (simulated)"
        )
    
    # Simular latencia de consulta (20-80ms)
    await simulate_latency(20, 80)
    
    if account_id not in ACCOUNTS:
        logger.warning(f"Request ID: {request_id} - Account {account_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found"
        )
    
    account = ACCOUNTS[account_id]
    logger.info(f"Request ID: {request_id} - Account {account_id} retrieved successfully")
    
    return AccountResponse(
        account_id=account["account_id"],
        holder_name=account["holder_name"],
        balance=account["balance"],
        currency=account["currency"],
        status=account["status"],
        timestamp=datetime.utcnow()
    )


@router.get("/{account_id}/balance", response_model=BalanceResponse)
async def get_balance(account_id: str, request: Request):
    """
    Consulta el saldo de una cuenta
    - Delay aleatorio: 20-80ms
    - 1% probabilidad de error 500
    - 404 si account_id no existe
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id} - GET /api/accounts/{account_id}/balance")
    
    # Simular error ocasional
    if simulate_error():
        logger.error(f"Request ID: {request_id} - Simulated 500 error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error (simulated)"
        )
    
    # Simular latencia de consulta (20-80ms)
    await simulate_latency(20, 80)
    
    if account_id not in ACCOUNTS:
        logger.warning(f"Request ID: {request_id} - Account {account_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Account {account_id} not found"
        )
    
    account = ACCOUNTS[account_id]
    logger.info(f"Request ID: {request_id} - Balance for account {account_id} retrieved")
    
    return BalanceResponse(
        account_id=account["account_id"],
        balance=account["balance"],
        currency=account["currency"],
        timestamp=datetime.utcnow()
    )

