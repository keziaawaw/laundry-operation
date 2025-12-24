from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class PriceRequest(BaseModel):
    weight_kg: float
    service_type: str
    note: Optional[str] = None


class PaymentWebhookPayload(BaseModel):
    transaction_id: str
    amount: float
    status: str
    timestamp: datetime


@router.post("/calculate")
def calculate_cost(req: PriceRequest):
    base_rate = 5000
    multipliers = {"regular": 1.0, "express": 1.5, "delicate": 1.2}

    mult = multipliers.get(req.service_type, 1.0)
    total = int(req.weight_kg * base_rate * mult)

    return {
        "weight_kg": req.weight_kg,
        "service_type": req.service_type,
        "base_rate": base_rate,
        "multiplier": mult,
        "total_amount": total,
        "currency": "IDR",
    }


@router.post("/payment/webhook")
def payment_webhook(payload: PaymentWebhookPayload):
    return {
        "status": "received",
        "transaction_id": payload.transaction_id,
        "message": "Notifikasi pembayaran diterima dan sedang diproses",
    }


@router.get("/status/{transaction_id}")
def get_payment_status(transaction_id: str):
    return {"transaction_id": transaction_id, "status": "pending", "amount": 0, "currency": "IDR"}
