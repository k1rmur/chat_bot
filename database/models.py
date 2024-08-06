from database.base import Base

from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, default=1)

    def __repr__(self):
        return f'UserModel(id={self.id!r}, username={self.username})'