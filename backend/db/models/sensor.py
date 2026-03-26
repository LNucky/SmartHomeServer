from datetime import datetime
from sqlalchemy import Float, DateTime, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sensor_name: Mapped[str] = mapped_column(String(50), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)  # для bool: 0.0 / 1.0
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # от ESP
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
