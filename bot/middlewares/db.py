from typing import Any, Awaitable, Callable, Dict

from database import Database
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from vkbottle import BaseMiddleware
from vkbottle.bot import Bot, Message


class DatabaseMiddleware(BaseMiddleware[Message]):
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self.session = session

    async def pre(self, event: Message, data: Dict[str, Any]) -> None:
        async with self.session() as session:
            db = Database(session=session)
            data['db'] = db

