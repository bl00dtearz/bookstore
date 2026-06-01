import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.book import Book, Author, Genre
from app.schemas.book import (
    BookCreate, BookUpdate, BookResponse,
    AuthorCreate, AuthorResponse,
    GenreCreate, GenreResponse,
)
from app.services.books import get_books, get_book_average_rating
from app.dependencies import get_current_user, require_admin
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/books", tags=["Books"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _build_book_response(book: Book, db: Session) -> BookResponse:
    avg = get_book_average_rating(db, book.id)
    data = BookResponse.model_validate(book)
    data.average_rating = avg
    return data


# ── Authors ───────────────────────────────────────────────────────────────────

@router.get("/authors", response_model=List[AuthorResponse], tags=["Authors"])
def list_authors(db: Session = Depends(get_db)):
    return db.query(Author).all()


@router.post("/authors", response_model=AuthorResponse, status_code=201, tags=["Authors"])
def create_author(payload: AuthorCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    author = Author(**payload.model_dump())
    db.add(author); db.commit(); db.refresh(author)
    return author


# ── Genres ────────────────────────────────────────────────────────────────────

@router.get("/genres", response_model=List[GenreResponse], tags=["Genres"])
def list_genres(db: Session = Depends(get_db)):
    return db.query(Genre).all()


@router.post("/genres", response_model=GenreResponse, status_code=201, tags=["Genres"])
def create_genre(payload: GenreCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Genre).filter(Genre.name == payload.name).first():
        raise HTTPException(400, "Genre already exists")
    genre = Genre(**payload.model_dump())
    db.add(genre); db.commit(); db.refresh(genre)
    return genre


# ── Books ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[BookResponse])
def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    author_id: Optional[int] = None,
    genre_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    books = get_books(db, skip, limit, search, author_id, genre_id, min_price, max_price)
    return [_build_book_response(b, db) for b in books]


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    return _build_book_response(book, db)


@router.post("", response_model=BookResponse, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    genres = db.query(Genre).filter(Genre.id.in_(payload.genre_ids)).all()
    book = Book(
        title=payload.title,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        cover_url=payload.cover_url,
        isbn=payload.isbn,
        author_id=payload.author_id,
        genres=genres,
    )
    db.add(book); db.commit(); db.refresh(book)
    logger.info("Book created: %s (id=%d)", book.title, book.id)
    return _build_book_response(book, db)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    update_data = payload.model_dump(exclude_unset=True)
    if "genre_ids" in update_data:
        book.genres = db.query(Genre).filter(Genre.id.in_(update_data.pop("genre_ids"))).all()
    for key, val in update_data.items():
        setattr(book, key, val)
    db.commit(); db.refresh(book)
    return _build_book_response(book, db)


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Book not found")
    db.delete(book); db.commit()
    logger.info("Book deleted: id=%d", book_id)
