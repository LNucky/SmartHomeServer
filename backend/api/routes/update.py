"""Единый эндпоинт для ESP: приём данных + ответ с состоянием устройств."""

from fastapi import APIRouter, HTTPException

from api.deps import DbSession
from api.schemas import UpdateRequest, UpdateResponse
from db.models import SENSOR_NAMES_BOOL, SENSOR_NAMES_FLOAT
from db.repositories.device_repo import DeviceRepository
from db.repositories.home_state_repo import HomeStateRepository
from db.repositories.sensor_repo import SensorRepository
from api.routes.scenario import recompute_devices_if_auto

router = APIRouter(tags=["update"])

VALID_SENSOR_NAMES = SENSOR_NAMES_FLOAT + SENSOR_NAMES_BOOL


@router.post("/update", response_model=UpdateResponse)
async def esp_update(data: UpdateRequest, db: DbSession):
    """
    ESP32 отправляет batch показаний.
    В ответе — актуальное состояние всех устройств (после пересчёта при auto_mode).
    """
    repo_sensor = SensorRepository(db)
    repo_device = DeviceRepository(db)
    h_repo = HomeStateRepository(db)

    count = 0
    for item in data.readings:
        if item.sensor_name not in VALID_SENSOR_NAMES:
            raise HTTPException(400, f"sensor_name должен быть один из: {VALID_SENSOR_NAMES}")
        await repo_sensor.create_reading(
            sensor_name=item.sensor_name,
            room_id=item.room_id,
            value=item.value,
            timestamp=data.timestamp,
        )
        count += 1

    await db.flush()
    await recompute_devices_if_auto(db)

    home = await h_repo.get()
    devices = await repo_device.get_all()
    device_states = [
        {"device_type": d.device_type, "room_id": d.room_id, "is_on": d.is_on}
        for d in devices
    ]

    await db.commit()
    return UpdateResponse(
        received=count,
        devices=device_states,
        scenario=home.scenario,
        auto_mode=home.auto_mode,
    )
