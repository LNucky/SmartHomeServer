"""
Расчёт состояний устройств по сценарию и показаниям датчиков.
ESP только получает готовые is_on.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Пороги (люксы — ориентир для BH1750-подобных датчиков; подстройте под стенд)
LUX_SUPPRESS_DAY_LIGHT = 400.0  # выше — дневной свет в гостиной не нужен (есть «естественная» лента)
TEMP_VENT_ON = 25.0
HUM_VENT_ON = 60.0

SCENARIOS = frozenset({"sunny", "cloudy", "night", "sleep"})


def _f(snapshot: dict[tuple[str, int], float], sensor: str, room: int, default: float | None = None) -> float | None:
    v = snapshot.get((sensor, room))
    if v is None:
        return default
    return v


def _movement(snapshot: dict[tuple[str, int], float], room: int) -> bool:
    v = _f(snapshot, "movement", room, 0.0)
    return v is not None and v >= 0.5


def _vent_for_room(snapshot: dict[tuple[str, int], float], room: int) -> bool:
    t = _f(snapshot, "temperature", room)
    h = _f(snapshot, "humidity", room)
    if t is not None and t > TEMP_VENT_ON:
        return True
    if h is not None and h > HUM_VENT_ON:
        return True
    return False


def compute_device_states(
    scenario: str,
    snapshot: dict[tuple[str, int], float],
) -> dict[tuple[str, int], bool]:
    """
    Возвращает карту (device_type, room_id) -> is_on для всех устройств из DEVICE_TYPES по комнатам.
    """
    from db.models import DEVICE_ALLOWED_ROOMS, DEVICE_TYPES

    states: dict[tuple[str, int], bool] = {}

    def set_dev(dtype: str, room: int, on: bool) -> None:
        if room in DEVICE_ALLOWED_ROOMS.get(dtype, (1, 2)):
            states[(dtype, room)] = on

    # Инициализация всем False
    for dt in DEVICE_TYPES:
        for room in DEVICE_ALLOWED_ROOMS.get(dt, (1, 2)):
            states[(dt, room)] = False

    if scenario == "sleep":
        return states

    if scenario == "night":
        set_dev("servo", 2, False)
        for room in (1, 2):
            set_dev("vent", room, _vent_for_room(snapshot, room))
            set_dev("socket_tv", room, False)
            set_dev("socket_ac", room, False)
            set_dev("day_light", room, False)
            set_dev("rgb", 1, False)
            set_dev("night_light", room, _movement(snapshot, room))
        return states

    if scenario == "sunny":
        set_dev("servo", 2, True)
        for room in (1, 2):
            set_dev("vent", room, _vent_for_room(snapshot, room))
            set_dev("socket_tv", room, True)
            set_dev("socket_ac", room, True)
            set_dev("night_light", room, False)
        set_dev("rgb", 1, True)
        lux1 = _f(snapshot, "light_level", 1)
        # Комната 1: при достаточной освещённости (лента светит на датчик) — дневной свет выкл даже при движении
        if lux1 is not None and lux1 > LUX_SUPPRESS_DAY_LIGHT:
            set_dev("day_light", 1, False)
        else:
            set_dev("day_light", 1, _movement(snapshot, 1))
        set_dev("day_light", 2, _movement(snapshot, 2))
        return states

    if scenario == "cloudy":
        set_dev("servo", 2, True)
        for room in (1, 2):
            set_dev("vent", room, _vent_for_room(snapshot, room))
            set_dev("socket_tv", room, True)
            set_dev("socket_ac", room, True)
            set_dev("night_light", room, False)
            set_dev("day_light", room, _movement(snapshot, room))
        set_dev("rgb", 1, False)
        return states

    # неизвестный сценарий — всё выкл
    return states
