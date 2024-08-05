from database.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Boolean


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    is_subscribed_to_oper = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'UserModel(id={self.id!r})'