import secrets
from datetime import datetime
from typing import Any, Dict, List

from beanie import Document, Insert, PydanticObjectId, Update, before_event
from pydantic import BaseModel, Field


class DeviceData(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any]

    class Settings:
        name = "device_data"


class DeviceDataCreate(BaseModel):
    device_id: str
    data: Dict[str, Any]


class Device(Document):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    created_date: datetime | None = None
    updated_date: datetime | None = None
    device_id: str
    api_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    data: List[DeviceData] = []

    @before_event(Insert)
    def set_times(self):
        self.created_date = datetime.now()
        self.updated_date = datetime.now()

    @before_event(Update)
    def update_time(self):
        self.updated_date = datetime.now()

    class Settings:
        name = "devices"


class DeviceCreate(BaseModel):
    device_id: str


class DevicePublic(BaseModel):
    id: PydanticObjectId
    created_date: datetime
    updated_date: datetime
    device_id: str
    data: List[DeviceData]
