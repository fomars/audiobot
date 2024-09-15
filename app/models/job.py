# app/models/job.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, update
from app.db import Base, utcnow, Session


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    frozen_amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())
    completed_at = Column(DateTime, nullable=True)

    @staticmethod
    def create(user_id: int, frozen_amount: int) -> int:
        with Session() as session:
            job = Job(user_id=user_id, frozen_amount=frozen_amount)
            session.add(job)
            session.commit()
            return job.id

    @staticmethod
    def mark_completed(id_: int) -> None:
        with Session() as session:
            query = update(Job).where(Job.id == id_).values(completed_at=utcnow())
            session.execute(query)
            session.commit()
