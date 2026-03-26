from datetime import datetime
from pydantic import BaseModel, Field


# --- Датчики ---

class SensorReadingItem(BaseModel):
    sensor_name: str = Field(
        ...,
        description="temperature, humidity, light_level (люксы), movement, gas",
    )
    room_id: int = Field(..., ge=1, description="id комнаты")
    value: float = Field(..., description="для bool: 0.0 или 1.0")


class UpdateRequest(BaseModel):
    """Запрос от ESP: batch показаний."""
    timestamp: datetime = Field(..., description="время с ESP")
    readings: list[SensorReadingItem] = Field(..., description="массив показаний")


class UpdateResponse(BaseModel):
    """Ответ ESP: сколько принято + актуальное состояние устройств."""
    received: int
    devices: list[dict]
    scenario: str
    auto_mode: bool


class SensorReadingResponse(BaseModel):
    id: int
    sensor_name: str
    room_id: int
    value: float
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class SensorLatestItem(BaseModel):
    sensor_name: str
    room_id: int
    value: float
    timestamp: str | None


# --- Устройства (night_light, day_light) ---

class DeviceStateResponse(BaseModel):
    id: int
    device_type: str
    room_id: int
    is_on: bool

    class Config:
        from_attributes = True


class DeviceCommandRequest(BaseModel):
    turn_on: bool


class ScenarioResponse(BaseModel):
    scenario: str
    auto_mode: bool


class ScenarioUpdateRequest(BaseModel):
    scenario: str | None = None
    auto_mode: bool | None = None
