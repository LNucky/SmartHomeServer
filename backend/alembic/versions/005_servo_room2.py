"""servo curtain only in room 2

Revision ID: 005
Revises: 004
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("""
            INSERT INTO devices (device_type, room_id, is_on) VALUES
            ('servo', 2, false)
            ON CONFLICT ON CONSTRAINT uq_device_room DO NOTHING
        """)
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM devices WHERE device_type = 'servo'"))
