from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import insert

from app.db import Base, utcnow, Session


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    tg_id = Column(BigInteger, primary_key=True, autoincrement=False)
    tg_username = Column(String(255))
    first_name = Column(String(255), nullable=False)
    is_bot = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())

    last_message_at = Column(
        DateTime, nullable=False, onupdate=utcnow(), server_default=utcnow(), index=True
    )


class UserDAL:
    @staticmethod
    def upsert_user(tg_id: int, first_name: str, is_bot: bool, tg_username: str = None):
        with Session() as session:
            user = User(tg_username=tg_username, first_name=first_name, is_bot=is_bot)
            user.tg_ig = tg_id

            query = (
                insert(User)
                .values(
                    tg_id=tg_id,
                    tg_username=tg_username,
                    first_name=first_name,
                    is_bot=is_bot,
                    last_message_at=utcnow(),
                )
                .on_conflict_do_update(
                    index_elements=["tg_id"],
                    set_={
                        "tg_id": tg_id,
                        "tg_username": tg_username,
                        "first_name": first_name,
                        "is_bot": is_bot,
                        "last_message_at": utcnow(),
                    },
                )
            )
            session.execute(query)
            session.commit()
