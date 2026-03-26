"""ESP: POST — приём показаний; GET — только чтение состояния устройств из БД."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api.deps import DbSession
from api.schemas import (
    DeviceSnapshotItem,
    UpdatePostResponse,
    UpdateRequest,
    UpdateSnapshotResponse,
)
from db.models import SENSOR_NAMES_BOOL, SENSOR_NAMES_FLOAT
from db.repositories.device_repo import DeviceRepository
from db.repositories.home_state_repo import HomeStateRepository
from db.repositories.sensor_repo import SensorRepository
from api.routes.scenario import recompute_devices_if_auto

router = APIRouter(tags=["update"])

VALID_SENSOR_NAMES = SENSOR_NAMES_FLOAT + SENSOR_NAMES_BOOL


async def _build_snapshot(db) -> UpdateSnapshotResponse:
    h_repo = HomeStateRepository(db)
    repo_device = DeviceRepository(db)
    home = await h_repo.get()
    devices = await repo_device.get_all()
    items = [
        DeviceSnapshotItem(device_type=d.device_type, room_id=d.room_id, is_on=d.is_on)
        for d in devices
    ]
    return UpdateSnapshotResponse(
        devices=items,
        scenario=home.scenario,
        auto_mode=home.auto_mode,
    )


@router.get("/update", response_model=UpdateSnapshotResponse)
async def esp_get_state(db: DbSession):
    """
    Текущее состояние всех устройств + сценарий (без записи датчиков).
    Удобно опрашивать чаще, чем отправлять POST с показаниями.
    """
    snap = await _build_snapshot(db)
    await db.commit()
    return snap


@router.post("/update", response_model=UpdatePostResponse)
async def esp_update(data: UpdateRequest, db: DbSession):
    """
    ESP32 отправляет batch показаний.
    В ответе только число принятых записей; состояние реле запрашивать GET /api/update.
    """
    repo_sensor = SensorRepository(db)
    received_at = datetime.now(timezone.utc)

    count = 0
    for item in data.readings:
        if item.sensor_name not in VALID_SENSOR_NAMES:
            raise HTTPException(400, f"sensor_name должен быть один из: {VALID_SENSOR_NAMES}")
        await repo_sensor.create_reading(
            sensor_name=item.sensor_name,
            room_id=item.room_id,
            value=item.value,
            timestamp=received_at,
        )
        count += 1

    await db.flush()
    await recompute_devices_if_auto(db)

    await db.commit()
    return UpdatePostResponse(received=count)
