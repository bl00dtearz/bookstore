from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ReviewCreate(BaseModel):
    rating: float
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_in_range(cls, v: float) -> float:
        if not (1.0 <= v <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0")
        return round(v, 1)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    book_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
