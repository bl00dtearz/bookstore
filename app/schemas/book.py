from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator


class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorResponse(AuthorBase):
    id: int
    model_config = {"from_attributes": True}


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
    model_config = {"from_attributes": True}


class BookCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    cover_url: Optional[str] = None
    isbn: Optional[str] = None
    author_id: Optional[int] = None
    genre_ids: List[int] = []

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("stock")
    @classmethod
    def stock_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock must be non-negative")
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    cover_url: Optional[str] = None
    author_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None


class BookResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    stock: int
    cover_url: Optional[str]
    isbn: Optional[str]
    author: Optional[AuthorResponse]
    genres: List[GenreResponse]
    average_rating: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
