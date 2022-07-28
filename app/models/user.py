from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.db import Base, utcnow


class User(Base):
    __tablename__ = "user"
    __mapper_args__ = {"eager_defaults": True}

    tg_ig = Column(Integer, primary_key=True)
    tg_username = Column(String(255))
    first_name = Column(String(255), nullable=False)
    is_bot = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())
    last_message_at = Column(DateTime, nullable=False, onupdate=utcnow())

