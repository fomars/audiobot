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
    def create(db_session: Session, user_id: int, file_path: str, audio_length: int) -> "Job":
        job = Job(
            user_id=user_id,
            audio_length_seconds=audio_length,
            file_path=file_path,
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job

    def mark_file_ready(self, db_session: Session, file_path: str) -> None:
        query = update(Job).where(Job.id == self.id).values(file_path=file_path)
        db_session.execute(query)
        db_session.commit()
        db_session.refresh(self)


    def mark_finished(self, db_session: Session, success: bool) -> None:
        query = update(Job).where(Job.id == self.id).values(success=success, completed_at=utcnow())
        db_session.execute(query)
        db_session.commit()
        db_session.refresh(self)
