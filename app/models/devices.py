import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class DeviceData(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any]

    class Settings:
        name = "device_data"


class DeviceDataCreate(BaseModel):
    device_id: str
    data: Dict[str, Any]


class Device(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    device_id: str
    api_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    data: List[DeviceData] = []

    async def save(self, *args, **kwargs):
        self.updated_date = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)

    class Settings:
        use_revision = True
        name = "devices"


class DeviceCreate(BaseModel):
    device_id: str


class DevicePublic(BaseModel):
    id: PydanticObjectId
    created_date: datetime
    updated_date: datetime
    device_id: str
    data: List[DeviceData]
