from fastapi import APIRouter, Depends

from app.auth import role_checker
from app.models.devices import Device
from app.models.users import User

router = APIRouter()


@router.post("/device", response_model=Device)
async def register_device(
    device: Device, user: User = Depends(role_checker(["admin"]))
):
    await device.insert()
    return device
