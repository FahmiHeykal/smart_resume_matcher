from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class MatchingLog(Base):
    __tablename__ = "matching_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Float, nullable=False)
    matched_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    resume = relationship("Resume")
    job = relationship("Job")
