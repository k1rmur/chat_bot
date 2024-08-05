from database.base import Base

from sqlalchemy import Column, String, BigInteger

class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    chat_id = Column(BigInteger)
    username = Column(String)

    def __repr__(self):
        return f'UserModel(id={self.id!r}, username={self.username}, chat_id={self.chat_id})'