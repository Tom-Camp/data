from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from beanie import (
    Document,
    Insert,
    Link,
    PydanticObjectId,
    Replace,
    Update,
    before_event,
)
from pydantic import BaseModel, Field

from app.models.users import User


class Entry(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    title: str
    date: datetime
    location: str
    body: str
    images: List[str]

    @before_event([Insert, Replace, Update])
    def set_date(self):
        if isinstance(self.date, str):
            try:
                self.date = datetime.strptime(self.date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.date = datetime.now()


class Journal(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    title: str
    author: Link[User]
    created_date: datetime | None = None
    updated_date: datetime | None = None
    description: str
    entries: List[Entry]

    @before_event(Insert)
    def set_times(self):
        self.created_date = datetime.now(ZoneInfo("America/New_York"))
        self.updated_date = datetime.now(ZoneInfo("America/New_York"))

    class Settings:
        name = "journals"
