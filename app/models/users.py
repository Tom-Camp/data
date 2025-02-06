from enum import Enum

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


class Role(Enum):
    ADMIN = 3
    EDITOR = (2,)
    AUTHENTICATED = 1


class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str
    email: str
    hashed_password: str
    role: Role

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserList(BaseModel):
    username: str
