import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse
from app.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Reviews"])


def _review_response(review: Review) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=review.user.name,
        book_id=review.book_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )


@router.get("/books/{book_id}/reviews", response_model=List[ReviewResponse])
def list_reviews(book_id: int, db: Session = Depends(get_db)):
    if not db.query(Book).filter(Book.id == book_id).first():
        raise HTTPException(404, "Book not found")
    reviews = db.query(Review).filter(Review.book_id == book_id).all()
    return [_review_response(r) for r in reviews]


@router.post("/books/{book_id}/reviews", response_model=ReviewResponse, status_code=201)
def create_review(
    book_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not db.query(Book).filter(Book.id == book_id).first():
        raise HTTPException(404, "Book not found")
    if db.query(Review).filter(Review.user_id == user.id, Review.book_id == book_id).first():
        raise HTTPException(400, "You have already reviewed this book")
    review = Review(user_id=user.id, book_id=book_id, rating=payload.rating, comment=payload.comment)
    db.add(review); db.commit(); db.refresh(review)
    logger.info("Review added: book_id=%d user_id=%d rating=%.1f", book_id, user.id, payload.rating)
    return _review_response(review)


@router.delete("/books/{book_id}/reviews/{review_id}", status_code=204)
def delete_review(
    book_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(Review.id == review_id, Review.book_id == book_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    if review.user_id != user.id:
        raise HTTPException(403, "You can only delete your own reviews")
    db.delete(review); db.commit()
