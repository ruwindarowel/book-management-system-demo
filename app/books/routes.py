from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetails
from ..db.db_main import get_session

from .services import BookService
from ..auth.auth_dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter(tags=["Books"])
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@book_router.get(
    "/", response_model=List[BookDetails], dependencies=[Depends(role_checker)]
)  # Have to define this using a List annotator to not throw error
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),  # Turns this into a protected endpoint
):
    books = await book_service.get_all_books(session)
    logging.info(f"{token_details} checked all books")
    return books


@book_router.get(
    "/user/{user_uid}", response_model=List[Book], dependencies=[Depends(role_checker)]
)  # Have to define this using a List annotator to not throw error
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),  # Turns this into a protected endpoint
):
    books = await book_service.get_user_books(user_uid, session)
    logging.info(f"{token_details} checked all books")
    return books


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[Depends(role_checker)],
)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    user_id = token_details.get("user")["user_uid"]
    logging.info(f"{token_details} created a book")
    new_book = await book_service.create_book(book_data, user_id, session)

    return new_book


@book_router.get(
    "/{book_uuid}",
    dependencies=[Depends(role_checker)],
)
async def get_book(
    book_uuid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    logging.info(f"{token_details} checked a book with uid {book_uuid}")
    book = await book_service.get_book(book_uuid, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )


@book_router.patch(
    "/{book_uuid}",
    dependencies=[Depends(role_checker)],
)
async def update_book(
    book_uuid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    logging.info(f"{token_details} updated a book with uid {book_uuid}")
    updated_book = await book_service.update_book(book_uuid, book_update_data, session)

    if updated_book:
        return updated_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )


@book_router.delete(
    "/{book_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_checker)],
)
async def delete_book(
    book_uuid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    logging.info(f"{token_details} deleted the book with uid {book_uuid}")
    book_to_delete = await book_service.delete_book(book_uuid, session)

    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book Not Found"
        )
    else:
        return {}
