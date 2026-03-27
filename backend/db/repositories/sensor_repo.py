from datetime import datetime

from sqlalchemy import func, select
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
        q = q.order_by(SensorReading.timestamp.desc())
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
            .order_by(SensorReading.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_latest_all_sensors(self, room_id: int | None = None) -> list[dict]:
        """Последнее значение для каждой пары (sensor_name, room_id)."""
        subq_sel = (
            select(
                SensorReading.sensor_name,
                SensorReading.room_id,
                func.max(SensorReading.timestamp).label("max_ts"),
            )
            .group_by(SensorReading.sensor_name, SensorReading.room_id)
        )
        if room_id is not None:
            subq_sel = subq_sel.where(SensorReading.room_id == room_id)
        subq = subq_sel.subquery()

        q = select(SensorReading).join(
            subq,
            (SensorReading.sensor_name == subq.c.sensor_name)
            & (SensorReading.room_id == subq.c.room_id)
            & (SensorReading.timestamp == subq.c.max_ts),
        )
        result = await self.db.execute(q)
        readings = list(result.scalars().all())
        return [
            {
                "sensor_name": r.sensor_name,
                "room_id": r.room_id,
                "value": r.value,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in readings
        ]

    async def get_snapshot_dict(self) -> dict[tuple[str, int], float]:
        """Последнее значение для каждой пары (sensor_name, room_id)."""
        subq = (
            select(
                SensorReading.sensor_name,
                SensorReading.room_id,
                func.max(SensorReading.timestamp).label("max_ts"),
            )
            .group_by(SensorReading.sensor_name, SensorReading.room_id)
        ).subquery()

        q = select(SensorReading).join(
            subq,
            (SensorReading.sensor_name == subq.c.sensor_name)
            & (SensorReading.room_id == subq.c.room_id)
            & (SensorReading.timestamp == subq.c.max_ts),
        )
        result = await self.db.execute(q)
        readings = list(result.scalars().all())
        return {(r.sensor_name, r.room_id): r.value for r in readings}
