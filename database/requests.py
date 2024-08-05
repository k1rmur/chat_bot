from database.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, id: int) -> None:
        user = await self.session.get(User, id)
        if not user:
            user = User(
                id=id
            )
            self.session.add(user)
        await self.session.commit()


    async def get_user_data(self, id: int) -> User:
        user = await self.session.get(User, id)
        return user


    async def get_all_users(self):
        stmt = select(User.chat_id).where()
        result = await self.session.execute(stmt)

        result = [i[0] for i in result.all()]
        return result

        

