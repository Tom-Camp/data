from datetime import datetime
from typing import List

from beanie import Document, Insert, Link, PydanticObjectId, Update, before_event
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
    created_date: datetime | None = None
    updated_date: datetime | None = None
    description: str
    entries: List[Entry]

    @before_event(Insert)
    async def set_times(self):
        self.created_date = datetime.now()
        self.updated_date = datetime.now()

    @before_event(Update)
    async def update_times(self):
        self.updated_date = datetime.now()

    class Settings:
        name = "journals"


class JournalCreate(BaseModel):
    title: str
    created_date: datetime | None = None
    updated_date: datetime | None = None
    author: Link[User]
    description: str
    entries: List[Entry]


class JournalUpdate(BaseModel):
    title: str
    description: str
    entries: List[Entry]
