from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("device_type", "room_id", name="uq_device_room"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # night_light, day_light, vent, socket_tv, socket_ac, servo, rgb
    room_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_on: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
