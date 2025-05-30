from pydantic import BaseModel, field_validator
import uuid
from datetime import datetime
from typing import List

from app.reviews.review_schemas import ReviewModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str

    created_at: datetime
    updated_at: datetime


class BookDetails(Book):
    reviews: List[ReviewModel]


class BookCreateModel(BaseModel):
    title: str
    publisher: str
    published_date: datetime
    page_count: int
    language: str

    @field_validator("published_date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            # Allow both "YYYY-MM-DD" and "YYYY/MM/DD"
            value = value.replace("/", "-")
            return datetime.strptime(value, "%Y-%m-%d")
        except Exception:
            raise ValueError("Invalid date format. Use YYYY-MM-DD or YYYY/MM/DD.")


class BookUpdateModel(BaseModel):
    title: str
    publisher: str
    page_count: int
    language: str
