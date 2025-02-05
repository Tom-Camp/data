from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models.devices import Device

router = APIRouter()


@router.post("/devices", response_model=Device)
async def create_journal(device: Device, current_user: str = Depends(get_current_user)):
    await device.insert()
    return device
