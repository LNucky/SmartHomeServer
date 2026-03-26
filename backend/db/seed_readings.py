"""Начальные показания датчиков, если таблица пуста (после миграций)."""

from datetime import datetime, timezone

from sqlalchemy import func, select

from db.database import async_session_maker
from db.models.sensor import SensorReading


async def seed_sensor_readings_if_empty() -> None:
    async with async_session_maker() as session:
        n = await session.scalar(select(func.count()).select_from(SensorReading))
        if n and n > 0:
            return
        ts = datetime.now(timezone.utc)
        rows = [
            SensorReading(sensor_name="temperature", room_id=1, value=23.5, timestamp=ts),
            SensorReading(sensor_name="temperature", room_id=2, value=21.8, timestamp=ts),
            SensorReading(sensor_name="humidity", room_id=1, value=58.0, timestamp=ts),
            SensorReading(sensor_name="humidity", room_id=2, value=55.0, timestamp=ts),
            SensorReading(sensor_name="light_level", room_id=1, value=780.0, timestamp=ts),
            SensorReading(sensor_name="movement", room_id=1, value=0.0, timestamp=ts),
            SensorReading(sensor_name="movement", room_id=2, value=0.0, timestamp=ts),
            SensorReading(sensor_name="gas", room_id=1, value=0.0, timestamp=ts),
            SensorReading(sensor_name="gas", room_id=2, value=0.0, timestamp=ts),
        ]
        session.add_all(rows)
        await session.commit()
