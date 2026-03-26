from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.device import Device


class DeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, device_type: str, room_id: int) -> Device:
        result = await self.db.execute(
            select(Device).where(
                Device.device_type == device_type,
                Device.room_id == room_id,
            ).limit(1)
        )
        device = result.scalar_one_or_none()
        if device is None:
            device = Device(device_type=device_type, room_id=room_id, is_on=False)
            self.db.add(device)
            await self.db.flush()
            await self.db.refresh(device)
        return device

    async def get(self, device_type: str, room_id: int) -> Device | None:
        result = await self.db.execute(
            select(Device).where(
                Device.device_type == device_type,
                Device.room_id == room_id,
            ).limit(1)
        )
        return result.scalar_one_or_none()

    async def set_state(self, device_type: str, room_id: int, is_on: bool) -> Device:
        device = await self.get_or_create(device_type, room_id)
        device.is_on = is_on
        await self.db.flush()
        await self.db.refresh(device)
        return device

    async def get_all(self) -> list[Device]:
        result = await self.db.execute(select(Device).order_by(Device.device_type, Device.room_id))
        return list(result.scalars().all())

    async def apply_computed_states(self, states: dict[tuple[str, int], bool]) -> None:
        """Применить рассчитанные состояния к существующим устройствам."""
        devices = await self.get_all()
        for d in devices:
            key = (d.device_type, d.room_id)
            if key in states:
                d.is_on = states[key]
