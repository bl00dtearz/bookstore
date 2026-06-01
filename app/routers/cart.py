import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.order import Cart, CartItem
from app.schemas.order import CartItemAdd, CartItemResponse, CartResponse
from app.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cart", tags=["Cart"])


def _get_or_create_cart(user: User, db: Session) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart); db.commit(); db.refresh(cart)
    return cart


def _cart_response(cart: Cart) -> CartResponse:
    items = []
    total = 0.0
    for item in cart.items:
        subtotal = item.quantity * item.book.price
        total += subtotal
        items.append(CartItemResponse(
            id=item.id,
            book_id=item.book_id,
            book_title=item.book.title,
            book_price=item.book.price,
            quantity=item.quantity,
            subtotal=subtotal,
        ))
    return CartResponse(id=cart.id, items=items, total=round(total, 2))


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(user, db)
    return _cart_response(cart)


@router.post("/items", response_model=CartResponse, status_code=201)
def add_item(payload: CartItemAdd, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == payload.book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    if book.stock < payload.quantity:
        raise HTTPException(400, f"Only {book.stock} copies in stock")

    cart = _get_or_create_cart(user, db)
    existing = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.book_id == payload.book_id).first()
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(CartItem(cart_id=cart.id, book_id=payload.book_id, quantity=payload.quantity))
    db.commit(); db.refresh(cart)
    return _cart_response(cart)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_item(item_id: int, payload: CartItemAdd, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    if item.book.stock < payload.quantity:
        raise HTTPException(400, f"Only {item.book.stock} copies in stock")
    item.quantity = payload.quantity
    db.commit(); db.refresh(cart)
    return _cart_response(cart)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(user, db)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item); db.commit(); db.refresh(cart)
    return _cart_response(cart)


@router.delete("", status_code=204)
def clear_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = _get_or_create_cart(user, db)
    for item in cart.items:
        db.delete(item)
    db.commit()
