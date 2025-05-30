from app.db.models import Review
from app.auth.auth_service import AuthService
from app.books.services import BookService
from .review_schemas import ReviewCreateModel

from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

book_service = BookService()
user_service = AuthService()


class ReviewService:

    async def add_review_to_book(
        self,
        user_email: str,
        book_uuid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uuid, session)
            user = await user_service.get_user_by_email(user_email, session)

            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book does not exist"
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()

            return new_review

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e
            )

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        reviews = await session.exec(statement)
        return reviews.all()
