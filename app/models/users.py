from enum import Enum
from typing import Annotated

from beanie import Indexed, PydanticObjectId
from pydantic import BaseModel, EmailStr

from app.models.base import AutoTimestampedDocument


class Role(Enum):
    ADMIN = 3
    EDITOR = 2
    AUTHENTICATED = 1


class User(AutoTimestampedDocument):
    username: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str
    role: Role = Role.AUTHENTICATED

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role = Role.AUTHENTICATED


class UserShow(BaseModel):
    id: PydanticObjectId
    username: str
    role: Role
