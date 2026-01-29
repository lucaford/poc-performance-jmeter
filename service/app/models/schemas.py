from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    """Request schema para crear una transferencia"""
    from_account: str = Field(..., description="ID de la cuenta origen")
    to_account: str = Field(..., description="ID de la cuenta destino")
    amount: float = Field(..., gt=0, description="Monto a transferir (debe ser positivo)")
    description: Optional[str] = Field(None, description="Descripción opcional de la transferencia")


class AccountResponse(BaseModel):
    """Response schema para información de cuenta"""
    account_id: str = Field(..., description="ID de la cuenta")
    holder_name: str = Field(..., description="Nombre del titular")
    balance: float = Field(..., description="Saldo actual")
    currency: str = Field(default="ARS", description="Moneda")
    status: str = Field(default="active", description="Estado de la cuenta")
    timestamp: datetime = Field(..., description="Timestamp de la respuesta")


class BalanceResponse(BaseModel):
    """Response schema para consulta de saldo"""
    account_id: str = Field(..., description="ID de la cuenta")
    balance: float = Field(..., description="Saldo actual")
    currency: str = Field(default="ARS", description="Moneda")
    timestamp: datetime = Field(..., description="Timestamp de la respuesta")


class TransferResponse(BaseModel):
    """Response schema para información de transferencia"""
    transfer_id: str = Field(..., description="ID único de la transferencia (UUID)")
    from_account: str = Field(..., description="ID de la cuenta origen")
    to_account: str = Field(..., description="ID de la cuenta destino")
    amount: float = Field(..., description="Monto transferido")
    status: str = Field(..., description="Estado: completed, pending, o failed")
    timestamp: datetime = Field(..., description="Timestamp de la transferencia")
    description: Optional[str] = Field(None, description="Descripción de la transferencia")


class ErrorResponse(BaseModel):
    """Response schema para errores"""
    error: str = Field(..., description="Tipo de error")
    detail: str = Field(..., description="Detalle del error")
    timestamp: datetime = Field(..., description="Timestamp del error")


class HealthResponse(BaseModel):
    """Response schema para health check"""
    status: str = Field(default="OK", description="Estado del servicio")
    timestamp: datetime = Field(..., description="Timestamp del health check")

