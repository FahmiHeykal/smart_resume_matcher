from pydantic import BaseModel

class ResumeSummaryCreate(BaseModel):
    resume_id: int
    summary: str
    skills: str

class ResumeSummaryOut(ResumeSummaryCreate):
    id: int

    class Config:
        from_attributes = True
