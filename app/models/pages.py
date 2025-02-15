from datetime import datetime, timezone

from beanie import Document, Link, PydanticObjectId
from pydantic import Field

from app.models.users import User


class Page(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    author: Link[User]
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    title: str
    body: str

    async def save(self, *args, **kwargs):
        self.updated_date = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    class Settings:
        use_revision = True
        name = "pages"
