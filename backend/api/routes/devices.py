from fastapi import APIRouter, HTTPException, Query

from api.deps import DbSession
from api.schemas import DeviceCommandRequest, DeviceStateResponse
from db.models import DEVICE_TYPES, device_allowed_rooms
from db.repositories.device_repo import DeviceRepository

router = APIRouter(prefix="/devices", tags=["devices"])


def _device_router(device_type: str, allowed_rooms: tuple[int, ...]):
    sub = APIRouter()

    def _check_room(room_id: int) -> None:
        if room_id not in allowed_rooms:
            raise HTTPException(
                status_code=400,
                detail=f"Для устройства «{device_type}» допустимы комнаты: {list(allowed_rooms)}",
            )

    @sub.get("", response_model=DeviceStateResponse)
    async def get_state(db: DbSession, room_id: int = Query(..., ge=1, le=2)):
        _check_room(room_id)
        repo = DeviceRepository(db)
        device = await repo.get_or_create(device_type, room_id)
        await db.commit()
        await db.refresh(device)
        return device

    @sub.post("", response_model=DeviceStateResponse)
    async def set_state(
        data: DeviceCommandRequest,
        db: DbSession,
        room_id: int = Query(..., ge=1, le=2),
    ):
        _check_room(room_id)
        repo = DeviceRepository(db)
        device = await repo.set_state(device_type, room_id, data.turn_on)
        await db.commit()
        await db.refresh(device)
        return device

    return sub


for dt in DEVICE_TYPES:
    router.include_router(_device_router(dt, device_allowed_rooms(dt)), prefix=f"/{dt}")


@router.get("", response_model=list[DeviceStateResponse])
async def get_all_devices(db: DbSession):
    """Все устройства (для фронта)."""
    repo = DeviceRepository(db)
    devices = await repo.get_all()
    await db.commit()
    return devices
