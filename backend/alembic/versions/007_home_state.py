"""home_state singleton

Revision ID: 007
Revises: 006
Create Date: 2026-03-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "home_state",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scenario", sa.String(20), nullable=False, server_default="sleep"),
        sa.Column("auto_mode", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(sa.text("INSERT INTO home_state (id, scenario, auto_mode) VALUES (1, 'sleep', true)"))


def downgrade() -> None:
    op.drop_table("home_state")
