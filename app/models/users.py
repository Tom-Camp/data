from datetime import datetime
from enum import Enum
from typing import Annotated
from zoneinfo import ZoneInfo

from beanie import Document, Indexed, Insert, PydanticObjectId, before_event
from pydantic import BaseModel, EmailStr, Field


class Role(Enum):
    ADMIN = 3
    EDITOR = 2
    AUTHENTICATED = 1


class User(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime | None = None
    updated_date: datetime | None = None
    username: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str
    role: Role = Role.AUTHENTICATED

    @before_event(Insert)
    def set_times(self):
        self.created_date = datetime.now(ZoneInfo("America/New_York"))
        self.updated_date = datetime.now(ZoneInfo("America/New_York"))

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
