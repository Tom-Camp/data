from fastapi import APIRouter, Depends

from app.auth import require_role
from app.models.devices import Device
from app.models.users import Role, User

router = APIRouter()


@router.post("/device", response_model=Device)
async def register_device(
    device: Device, user: User = Depends(require_role(Role.ADMIN))
):
    await device.insert()
    return device
