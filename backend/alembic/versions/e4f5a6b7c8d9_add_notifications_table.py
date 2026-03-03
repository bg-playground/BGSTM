"""add notifications table

Revision ID: e4f5a6b7c8d9
Revises: c2d3e4f5a6b7
Create Date: 2026-02-26 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum(
                "suggestions_generated",
                "coverage_drop",
                "suggestion_reviewed",
                "requirement_created",
                "test_case_created",
                name="notificationtype",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    sa.Enum(name="notificationtype").drop(op.get_bind(), checkfirst=True)
