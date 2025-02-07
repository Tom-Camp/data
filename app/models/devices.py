import secrets
from typing import Any, Dict

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Device(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    device_id: str
    api_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))

    class Settings:
        name = "devices"


class DeviceCreate(BaseModel):
    device_id: str
    api_key: str


class DeviceData(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    device_id: str
    data: Dict[str, Any]
