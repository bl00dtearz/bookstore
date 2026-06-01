"""
Mock payment service — simulates a payment gateway.
Returns a fake payment_id for any charge request.
"""
import uuid
import logging
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Mock Payment Service")


class PayRequest(BaseModel):
    amount: float
    currency: str = "USD"


@app.post("/pay")
def pay(req: PayRequest):
    payment_id = f"mock-{uuid.uuid4().hex[:12]}"
    logging.info("Mock payment processed: %s %.2f %s", payment_id, req.amount, req.currency)
    return {"payment_id": payment_id, "status": "success", "amount": req.amount}


@app.get("/health")
def health():
    return {"status": "ok"}
