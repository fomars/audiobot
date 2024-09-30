from sqlalchemy import Column, Integer, ForeignKey, DateTime, BigInteger, update, String, Boolean
from app.db import Base, utcnow, Session


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    audio_length_seconds = Column(Integer, nullable=False)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=utcnow())
    completed_at = Column(DateTime, nullable=True)
    success = Column(Boolean, nullable=True)

    @staticmethod
    def create(user_id: int, file_path: str, audio_length: int) -> int:
        with Session() as session:
            job = Job(
                user_id=user_id,
                audio_length_seconds=audio_length,
                file_path=file_path,
            )
            session.add(job)
            session.commit()
            return job.id

    @staticmethod
    def mark_completed(id_: int, success: bool) -> None:
        with Session() as session:
            query = update(Job).where(Job.id == id_).values(completed_at=utcnow())
            session.execute(query)
            session.commit()
