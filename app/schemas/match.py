from pydantic import BaseModel

class MatchResultCreate(BaseModel):
    resume_id: int
    job_id: int

class MatchResultOut(BaseModel):
    resume_id: int
    job_id: int
    score: float

    model_config = {
        "from_attributes": True
    }

class MatchResultWithJobOut(BaseModel):
    resume_id: int
    job_id: int
    score: float
    job_title: str
    job_description: str
    location: str
    category: str

    class Config:
        from_attributes  = True