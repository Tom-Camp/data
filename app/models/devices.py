import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.models.base import AutoTimestampedDocument


class DeviceData(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any]

    class Settings:
        name = "device_data"


class DeviceDataCreate(BaseModel):
    device_id: str
    data: Dict[str, Any]


class Device(AutoTimestampedDocument):
    device_id: str
    api_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    notes: dict = {}
    data: List[DeviceData] = []

    class Settings:
        name = "devices"


class DeviceCreate(BaseModel):
    device_id: str
    notes: dict = {}


class DevicePublic(BaseModel):
    _id: PydanticObjectId
    created_date: datetime
    updated_date: datetime
    device_id: str
    notes: dict
    data: List[DeviceData]
