from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ResumeSummary(Base):
    __tablename__ = "resume_summaries"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    summary = Column(Text, nullable=False)

    resume = relationship("Resume", back_populates="summary_data")
