from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    candidate = "candidate"
    admin = "admin"

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    role: UserRole

    model_config = {
        "from_attributes": True
    }
