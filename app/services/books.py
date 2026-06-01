from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.book import Book, Author, Genre


def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    author_id: Optional[int] = None,
    genre_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[Book]:
    query = db.query(Book)

    if search:
        pattern = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Book.title).like(pattern)
        )
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if genre_id:
        query = query.filter(Book.genres.any(Genre.id == genre_id))
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    return query.offset(skip).limit(limit).all()


def get_book_average_rating(db: Session, book_id: int) -> Optional[float]:
    from app.models.review import Review
    result = db.query(func.avg(Review.rating)).filter(Review.book_id == book_id).scalar()
    return round(float(result), 2) if result else None
