from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import Base, utcnow, get_session


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    tg_id = Column(Integer, primary_key=True, autoincrement=False)
    tg_username = Column(String(255))
    first_name = Column(String(255), nullable=False)
    is_bot = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())

    last_message_at = Column(DateTime, nullable=False, onupdate=utcnow(), server_default=utcnow(), index=True)


class UserDAL:
    @staticmethod
    async def upsert_user(tg_id: int, first_name: str, is_bot: bool, tg_username: str = None):
        async with get_session() as session:
            user = User(tg_username=tg_username, first_name=first_name, is_bot=is_bot)
            user.tg_ig = tg_id

            query = insert(User). \
                values(tg_id=tg_id,
                       tg_username=tg_username,
                       first_name=first_name,
                       is_bot=is_bot).\
                on_conflict_do_update(
                    index_elements=["tg_id"],
                    set_={
                        'tg_id': tg_id,
                        'tg_username': tg_username,
                        'first_name': first_name,
                        'is_bot': is_bot,
                        'last_message_at': utcnow()
                    })
            await session.execute(query)
            await session.commit()
