from beanie import Link
from pydantic import BaseModel

from app.models.base import AutoTimestampedDocument
from app.models.users import User


class Page(AutoTimestampedDocument):
    author: Link[User]
    title: str
    body: str

    class Settings:
        name = "pages"


class PageCreate(BaseModel):
    title: str
    body: str
