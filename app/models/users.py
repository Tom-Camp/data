from enum import Enum
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field


class Role(Enum):
    ADMIN = 3
    EDITOR = 2
    AUTHENTICATED = 1


class UserCreate(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    username: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str
    role: Role = Role.AUTHENTICATED

    class Settings:
        name = "users"


class User(Document):
    id: PydanticObjectId
    username: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    role: Role

    class Settings:
        name = "users"
