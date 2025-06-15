from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base  
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="resumes")
    summary_data = relationship("ResumeSummary", back_populates="resume", uselist=False)
    match_results = relationship("MatchResult", back_populates="resume")