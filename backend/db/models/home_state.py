from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class HomeState(Base):
    """Одна строка (id=1): текущий сценарий и глобальный авто-режим."""

    __tablename__ = "home_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario: Mapped[str] = mapped_column(String(20), nullable=False, default="sleep")
    auto_mode: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
