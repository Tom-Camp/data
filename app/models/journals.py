from datetime import datetime
from typing import List

from beanie import Link, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

from app.models.base import AutoTimestampedDocument
from app.models.users import User


class Entry(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    title: str
    date: datetime
    location: str
    body: str
    images: List[str]

    @field_validator("date", mode="before")
    def set_date(cls, v):
        if not v:
            return datetime.now()

        if isinstance(v, datetime):
            return v

        try:
            return datetime.fromisoformat(str(v))
        except (ValueError, TypeError):
            return datetime.now()


class Journal(AutoTimestampedDocument):
    title: str
    author: Link[User]
    description: str
    entries: List[Entry]

    class Settings:
        name = "journals"


class JournalCreate(BaseModel):
    title: str
    description: str
    entries: List[Entry]


class JournalUpdate(BaseModel):
    title: str
    description: str
    entries: List[Entry]
