from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .books.routes import book_router
from .auth.auth_routers import auth_router
from .reviews.review_routes import review_router
from contextlib import asynccontextmanager
from .db.db_main import init_db
import logging

origins = [
    "http://localhost:5173",
]


# Creating connection within the database
@asynccontextmanager
async def life_span(app: FastAPI):
    logging.info("SERVER IS STARTING.......")
    await init_db()
    yield
    logging.info("SERVER HAS STOPPED")


version = "v1"
app = FastAPI(
    title="Bookly",
    description="Trial API for books",
    version="v1",  # lifespan=life_span
    terms_of_service="",
    redoc_url=f"/{version}/redoc",
    openapi_url=f"/{version}/openapi.json",
    contact={"email": "test@test.com"},
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(book_router, prefix="/books")
app.include_router(auth_router, prefix="/auth")
app.include_router(review_router, prefix="/reviews")
