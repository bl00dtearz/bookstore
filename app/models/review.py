from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)   # 1.0 – 5.0
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1.0 AND rating <= 5.0", name="ck_review_rating"),
        UniqueConstraint("user_id", "book_id", name="uq_user_book_review"),
    )
