"""add item ai tasks table

Revision ID: 3d6e5d4e3b2a
Revises: 9eb552e21a67
Create Date: 2026-03-28 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3d6e5d4e3b2a"
down_revision: Union[str, Sequence[str], None] = "9eb552e21a67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "item_ai_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("task_type", sa.String(length=32), nullable=False),
        sa.Column("input_type", sa.String(length=32), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("UpdatedAt", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("CreatedAt", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_item_ai_tasks_item_id"), "item_ai_tasks", ["item_id"], unique=False)
    op.create_index(op.f("ix_item_ai_tasks_owner_id"), "item_ai_tasks", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_item_ai_tasks_owner_id"), table_name="item_ai_tasks")
    op.drop_index(op.f("ix_item_ai_tasks_item_id"), table_name="item_ai_tasks")
    op.drop_table("item_ai_tasks")

