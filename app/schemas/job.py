from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str
    location: str | None = None

class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_skills: str | None = None
    location: str | None = None

class JobOut(JobCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
