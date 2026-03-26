from datetime import datetime
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.sensor import SensorReading


class SensorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reading(
        self,
        sensor_name: str,
        room_id: int,
        value: float,
        timestamp: datetime,
    ) -> SensorReading:
        reading = SensorReading(
            sensor_name=sensor_name,
            room_id=room_id,
            value=value,
            timestamp=timestamp,
        )
        self.db.add(reading)
        await self.db.flush()
        await self.db.refresh(reading)
        return reading

    async def get_latest(
        self,
        sensor_name: str | None = None,
        room_id: int | None = None,
    ) -> list[SensorReading]:
        """Последние показания по каждому датчику (опционально фильтр по room)."""
        q = select(SensorReading)
        if sensor_name:
            q = q.where(SensorReading.sensor_name == sensor_name)
        if room_id is not None:
            q = q.where(SensorReading.room_id == room_id)
        q = q.order_by(desc(SensorReading.timestamp))
        result = await self.db.execute(q.limit(100))
        return list(result.scalars().all())

    async def get_latest_by_sensor_and_room(
        self,
        sensor_name: str,
        room_id: int,
    ) -> SensorReading | None:
        result = await self.db.execute(
            select(SensorReading)
            .where(
                SensorReading.sensor_name == sensor_name,
                SensorReading.room_id == room_id,
            )
            .order_by(desc(SensorReading.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_all_sensors(self, room_id: int | None = None) -> list[dict]:
        """Последнее значение каждого датчика (sensor_name, room_id)."""
        q = select(SensorReading)
        if room_id is not None:
            q = q.where(SensorReading.room_id == room_id)
        # Берём последнее по timestamp для каждой пары (sensor_name, room_id)
        # через подзапрос - проще итерацией
        result = await self.db.execute(
            q.order_by(desc(SensorReading.timestamp)).limit(50)
        )
        readings = list(result.scalars().all())
        seen: set[tuple[str, int]] = set()
        out: list[dict] = []
        for r in readings:
            key = (r.sensor_name, r.room_id)
            if key not in seen:
                seen.add(key)
                out.append({
                    "sensor_name": r.sensor_name,
                    "room_id": r.room_id,
                    "value": r.value,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                })
        return out

    async def get_snapshot_dict(self) -> dict[tuple[str, int], float]:
        """Последнее значение для каждой пары (sensor_name, room_id)."""
        result = await self.db.execute(
            select(SensorReading).order_by(desc(SensorReading.timestamp)).limit(200)
        )
        readings = list(result.scalars().all())
        seen: set[tuple[str, int]] = set()
        out: dict[tuple[str, int], float] = {}
        for r in readings:
            key = (r.sensor_name, r.room_id)
            if key not in seen:
                seen.add(key)
                out[key] = r.value
        return out
