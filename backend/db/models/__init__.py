from db.models.device import Device
from db.models.home_state import HomeState
from db.models.sensor import SensorReading

__all__ = ["SensorReading", "Device", "HomeState"]

# Датчики с ESP (gas/movement всегда шлются; light_level — люксы, комн. 1)
SENSOR_NAMES_FLOAT = ("temperature", "humidity", "light_level")
SENSOR_NAMES_BOOL = ("movement", "gas")

# Управляемые устройства (is_on в ответе /update и API)
DEVICE_TYPES = (
    "night_light",
    "day_light",
    "vent",
    "socket_tv",
    "socket_ac",
    "servo",  # штора (сервопривод), только комната 2
    "rgb",  # RGB-подсветка, только комната 1
)

# Если типа нет в словаре — комнаты 1 и 2
DEVICE_ALLOWED_ROOMS: dict[str, tuple[int, ...]] = {
    "servo": (2,),
    "rgb": (1,),
}


def device_allowed_rooms(device_type: str) -> tuple[int, ...]:
    return DEVICE_ALLOWED_ROOMS.get(device_type, (1, 2))
