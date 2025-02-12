from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_role, validate_api_key
from app.models.devices import (
    Device,
    DeviceCreate,
    DeviceData,
    DeviceDataCreate,
    DevicePublic,
)
from app.models.users import Role, User

router = APIRouter()


@router.post("/devices", response_model=Device)
async def register_device(
    device: DeviceCreate, user: User = Depends(require_role(Role.ADMIN))
):
    new_device = Device(**device.model_dump())
    await new_device.insert()
    return new_device


@router.post("/devices/data")
async def post_device_data(
    device_data: DeviceDataCreate, device: Device = Depends(validate_api_key)
):
    if device.device_id != device_data.device_id:
        raise HTTPException(status_code=401, detail="Mismatched device ID")

    device.data.append(DeviceData(data=device_data.data))
    await device.save()
    return {"message": "Data received"}


@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: PydanticObjectId):
    device = await Device.get(device_id)
    return device


@router.get("/devices/{device_id}/key")
async def get_device_api_key(
    device_id: PydanticObjectId, user: User = Depends(require_role(Role.ADMIN))
) -> str:
    device = await Device.get(device_id)
    return device.api_key


@router.get("/devices", response_model=list[DevicePublic])
async def list_devices():
    devices = await Device.find_all().to_list()
    return devices


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: PydanticObjectId, user: User = Depends(require_role(Role.ADMIN))
):
    existing_device = await Device.get(device_id)
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")

    await existing_device.delete()
    return {"message": "Device deleted successfully"}
