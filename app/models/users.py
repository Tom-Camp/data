from datetime import datetime, timezone
from enum import Enum
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, EmailStr, Field


class Role(Enum):
    ADMIN = 3
    EDITOR = 2
    AUTHENTICATED = 1


class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    username: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str
    role: Role = Role.AUTHENTICATED

    async def save(self, *args, **kwargs):
        self.updated_date = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    class Settings:
        use_revision = True
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
