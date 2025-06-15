from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=True)     
    category = Column(String, nullable=True)    
      
    match_results = relationship("MatchResult", back_populates="job")
    resume_matches = relationship("ResumeMatch", back_populates="job")
