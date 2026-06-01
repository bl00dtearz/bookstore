from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.order import OrderStatus


class CartItemAdd(BaseModel):
    book_id: int
    quantity: int = 1

    @field_validator("quantity")
    @classmethod
    def qty_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class CartItemResponse(BaseModel):
    id: int
    book_id: int
    book_title: str
    book_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total: float

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    shipping_address: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    book_id: Optional[int]
    book_title: Optional[str]
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_price: float
    shipping_address: Optional[str]
    payment_id: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
