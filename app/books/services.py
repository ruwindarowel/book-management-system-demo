from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc

from .schemas import BookCreateModel, BookUpdateModel
from ..db.models import Book
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uuid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uuid)

        result = await session.exec(statement)
        return result.first()

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid

        session.add(new_book)

        await session.commit()  # Adding a book to the database session

        return new_book

    async def update_book(
        self, book_uuid: str, update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uuid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(
                    book_to_update, k, v
                )  # Get object and update it based on the keys and values we provide it

            await session.commit()

            return book_to_update
        else:
            return None

    async def delete_book(self, book_uuid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uuid, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)

            await session.commit()

            return {}

        else:
            return None
