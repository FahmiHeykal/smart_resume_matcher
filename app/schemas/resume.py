from pydantic import BaseModel

class ResumeOut(BaseModel):
    id: int
    filename: str
    content: str
    user_id: int
    summary: str | None = None
    skills: str | None = None

    model_config = {
        "from_attributes": True
    }
