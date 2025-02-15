from datetime import datetime, timezone
from typing import List

from beanie import Document, Link, PydanticObjectId
from pydantic import BaseModel, Field, field_validator

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


class Journal(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    title: str
    author: Link[User]
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str
    entries: List[Entry]

    async def save(self, *args, **kwargs):
        self.updated_date = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    class Settings:
        use_revision = True
        name = "journals"


class JournalCreate(BaseModel):
    title: str
    author: Link[User]
    description: str
    entries: List[Entry]


class JournalUpdate(BaseModel):
    title: str
    description: str
    entries: List[Entry]
