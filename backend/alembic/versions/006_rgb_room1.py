"""rgb strip only in room 1

Revision ID: 006
Revises: 005
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO devices (device_type, room_id, is_on) VALUES
            ('rgb', 1, false)
            ON CONFLICT ON CONSTRAINT uq_device_room DO NOTHING
        """)
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM devices WHERE device_type = 'rgb'"))
