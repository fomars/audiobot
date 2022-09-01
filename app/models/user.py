from enum import Enum

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import insert, ENUM

from app.db import Base, utcnow, Session


class SubscriptionPlan(str, Enum):
    free = "free"
    limited = "limited"
    max = "max"


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
    subscription_plan = Column(
        ENUM(SubscriptionPlan, name="subscription_plan"),
        nullable=False,
        server_default=SubscriptionPlan.free,
    )
    subscription_ends_at = Column(DateTime, nullable=False, server_default="infinity")


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
            ).returning(*User.__table__.c)
            result_row = session.execute(query).fetchall()
            session.commit()
            return result_row
