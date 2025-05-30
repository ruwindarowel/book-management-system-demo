from ..db.models import User
from .auth_schemas import UserCreateModel
from .auth_utils import generate_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)
        return result.first()

    async def get_user_by_username(self, username: str, session: AsyncSession):
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        return result.first()

    async def user_exists(self, email: str, username: str, session: AsyncSession):
        user_email = await self.get_user_by_email(email, session)
        username = await self.get_user_by_username(username, session)
        if username is not None and user_email is not None:
            return True
        else:
            return False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        new_user.role = "user"

        session.add(new_user)
        await session.commit()

        return new_user
