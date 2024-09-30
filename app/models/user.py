from typing import Union

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import insert

from app.db import Base, utcnow, Session
from app.settings import app_settings


class User(Base):
    __tablename__ = "users"
    __mapper_args__ = {"eager_defaults": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True)
    tg_username = Column(String(255))
    first_name = Column(String(255), nullable=False)
    is_bot = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())
    last_message_at = Column(
        DateTime, nullable=False, onupdate=utcnow(), server_default=utcnow(), index=True
    )
    balance_seconds = Column(BigInteger, nullable=False, default=0, server_default="0")


class InsufficientBalanceError(ValueError):
    def __init__(self, user_id: int, balance: int, required: int):
        self.user_id = user_id
        self.balance = balance
        self.required = required
        super().__init__(f"User {user_id} has insufficient balance: {balance} < {required}")


class UserDAL:
    @staticmethod
    def upsert_user(tg_id: int, first_name: str, is_bot: bool, tg_username: str = None) -> User:
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
                    balance_seconds=app_settings.free_balance_seconds,
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
            ).returning(*User.__table__.c)
            result_row = session.execute(query).fetchone()
            session.commit()
            return result_row

    @staticmethod
    def deduct_balance(user_id: int, amount: int) -> Union[bool, int]:
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).one()
            if user.balance_seconds < amount:
                raise InsufficientBalanceError(user_id, user.balance_seconds, amount)
            user.balance_seconds -= amount
            session.commit()
            return True

    @staticmethod
    def top_up_balance(user_id: int, amount: int) -> None:
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).one()
            user.balance_seconds += amount
            session.commit()
