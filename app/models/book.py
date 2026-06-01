from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Table, Index
from sqlalchemy.orm import relationship

from app.database import Base


# Many-to-many: books <-> genres
book_genre = Table(
    "book_genre",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    bio = Column(Text, nullable=True)

    books = relationship("Book", back_populates="author")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    books = relationship("Book", secondary=book_genre, back_populates="genres")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    cover_url = Column(String(500), nullable=True)
    isbn = Column(String(20), unique=True, nullable=True)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    author = relationship("Author", back_populates="books")
    genres = relationship("Genre", secondary=book_genre, back_populates="books")
    order_items = relationship("OrderItem", back_populates="book")
    cart_items = relationship("CartItem", back_populates="book")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

    # Composite index for common searches
    __table_args__ = (
        Index("ix_books_title_price", "title", "price"),
    )
