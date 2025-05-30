from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.auth_dependencies import RoleChecker
from app.db.models import User
from app.db.db_main import get_session
from app.auth.auth_dependencies import get_current_user
from .review_schemas import ReviewCreateModel
from .review_service import ReviewService

review_service = ReviewService()
review_router = APIRouter(tags=["Reviews"])
role_checker = RoleChecker(["user", "admin"])


@review_router.post("/review/{book_uuid}")
async def add_review_to_books(
    book_uuid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        current_user.email, book_uuid, review_data, session
    )

    return new_review


@review_router.get("/", dependencies=[Depends(role_checker)])
async def get_all_reviews(
    session: AsyncSession = Depends(get_session),
):
    book_reviews = await review_service.get_all_reviews(session)

    return book_reviews
