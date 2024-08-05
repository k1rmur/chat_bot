from database.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column()
    username: Mapped[str] = mapped_column()

    def __repr__(self):
        return f'UserModel(id={self.id!r}, username={self.username}, chat_id={self.chat_id})'