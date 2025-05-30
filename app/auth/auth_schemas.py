from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from typing import List

from app.books.schemas import Book
from app.reviews.review_schemas import ReviewModel


class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(
        exclude=True
    )  # We keep this and remove everything else related to the database
    created_at: datetime
    updated_at: datetime


class UserBookModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)
