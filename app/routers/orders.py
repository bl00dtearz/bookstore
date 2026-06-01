import logging
import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.order import Cart, Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse, OrderStatusUpdate
from app.dependencies import get_current_user, require_admin
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


def _order_response(order: Order) -> OrderResponse:
    items = []
    for item in order.items:
        items.append(OrderItemResponse(
            id=item.id,
            book_id=item.book_id,
            book_title=item.book.title if item.book else "Deleted book",
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=round(item.quantity * item.unit_price, 2),
        ))
    return OrderResponse(
        id=order.id,
        status=order.status,
        total_price=order.total_price,
        shipping_address=order.shipping_address,
        payment_id=order.payment_id,
        items=items,
        created_at=order.created_at,
    )


def _call_payment_mock(total: float) -> str:
    """Call the mock payment service. Returns a fake payment_id."""
    try:
        resp = httpx.post(
            f"{settings.PAYMENT_MOCK_URL}/pay",
            json={"amount": total, "currency": "USD"},
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json().get("payment_id", "mock-payment-ok")
    except Exception as exc:
        logger.warning("Payment mock unreachable, using fallback: %s", exc)
        return "mock-payment-fallback"


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty — add books before placing an order")

    # Validate stock and calculate total
    total = 0.0
    for item in cart.items:
        if item.book.stock < item.quantity:
            raise HTTPException(400, f"'{item.book.title}' has only {item.book.stock} copies left")
        total += item.quantity * item.book.price

    # Mock payment
    payment_id = _call_payment_mock(total)

    # Create order
    order = Order(
        user_id=user.id,
        status=OrderStatus.paid,
        total_price=round(total, 2),
        shipping_address=payload.shipping_address,
        payment_id=payment_id,
    )
    db.add(order); db.flush()

    # Create order items and decrement stock
    for item in cart.items:
        db.add(OrderItem(
            order_id=order.id,
            book_id=item.book_id,
            quantity=item.quantity,
            unit_price=item.book.price,
        ))
        item.book.stock -= item.quantity

    # Clear cart
    for item in cart.items:
        db.delete(item)

    db.commit(); db.refresh(order)
    logger.info("Order placed: id=%d user=%d total=%.2f", order.id, user.id, total)
    return _order_response(order)


@router.get("", response_model=List[OrderResponse])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    return [_order_response(o) for o in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return _order_response(order)


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = payload.status
    db.commit(); db.refresh(order)
    logger.info("Order %d status updated to %s", order_id, payload.status)
    return _order_response(order)
