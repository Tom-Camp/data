from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str
    email: str
    hashed_password: str

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
