from database.models import User

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, id: int, chat_id: int, username: str) -> None:
        user = await self.session.get(User, id)
        if not user:
            user = User(
                id=id,
                chat_id=chat_id,
                username=username,
            )
            self.session.add(user)
        await self.session.commit()


    async def get_chat_ids(self):
        result = await self.session.query(User).all()

        return [user.chat_id for user in result]


        

