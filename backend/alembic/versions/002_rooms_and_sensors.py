"""rooms and sensors

Revision ID: 002
Revises: 001
Create Date: 2025-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("commands")
    op.drop_table("devices")
    op.drop_table("sensor_readings")

    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sensor_name", sa.String(50), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sensor_readings_room_name", "sensor_readings", ["room_id", "sensor_name"])

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("is_on", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_type", "room_id", name="uq_device_room"),
    )
    op.create_table(
        "commands",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Создаём night_light и day_light для комнат 1 и 2
    op.execute(
        sa.text("""
            INSERT INTO devices (device_type, room_id, is_on)
            VALUES 
                ('night_light', 1, false), ('night_light', 2, false),
                ('day_light', 1, false), ('day_light', 2, false)
        """)
    )


def downgrade() -> None:
    op.drop_table("commands")
    op.drop_table("devices")
    op.drop_table("sensor_readings")

    op.create_table(
        "sensor_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sensor_type", sa.String(50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_on", sa.Boolean(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "commands",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
