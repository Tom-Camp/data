import secrets
from typing import Any, Dict, List

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class DeviceData(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    data: Dict[str, Any]


class Device(Document):
    id: PydanticObjectId
    device_id: str
    api_key: str
    data: List[DeviceData] | None

    class Settings:
        name = "devices"


class DeviceCreate(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    device_id: str
    api_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    data: List[DeviceData] | None

    class Settings:
        name = "devices"
