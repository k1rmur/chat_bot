from database.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class Database:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user(self, id: int, username: str) -> None:
        user = await self.session.get(User, id)
        if not user:
            user = User(
                id=id,
                username=username,
            )
            self.session.add(user)
        await self.session.commit()


    async def get_chat_ids(self):
        stmt = select(User.id)
        try:
            result = await self.session.execute(stmt)
        except Exception as e:
            print(e)
        return [user[0] for user in result.all()]


        

