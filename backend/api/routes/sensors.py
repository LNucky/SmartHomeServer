from fastapi import APIRouter, HTTPException, Query

from api.deps import DbSession
from api.schemas import SensorLatestItem, SensorReadingResponse
from db.models import SENSOR_NAMES_BOOL, SENSOR_NAMES_FLOAT
from db.repositories.sensor_repo import SensorRepository

router = APIRouter(prefix="/sensors", tags=["sensors"])

VALID_SENSOR_NAMES = SENSOR_NAMES_FLOAT + SENSOR_NAMES_BOOL


@router.get("/latest", response_model=list[SensorLatestItem])
async def get_latest_readings(
    db: DbSession,
    room_id: int | None = Query(None, description="Фильтр по комнате"),
):
    """Последние показания всех датчиков (опционально по комнате)."""
    repo = SensorRepository(db)
    items = await repo.get_latest_all_sensors(room_id=room_id)
    return [SensorLatestItem(**x) for x in items]


@router.get("/latest/{sensor_name}", response_model=SensorReadingResponse | None)
async def get_latest_by_sensor(
    sensor_name: str,
    db: DbSession,
    room_id: int = Query(..., description="id комнаты"),
):
    """Последнее значение конкретного датчика в комнате."""
    if sensor_name not in VALID_SENSOR_NAMES:
        raise HTTPException(400, f"sensor_name должен быть один из: {VALID_SENSOR_NAMES}")
    repo = SensorRepository(db)
    return await repo.get_latest_by_sensor_and_room(sensor_name, room_id)
