"""add type and title columns to notifications table

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-02-26 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    notification_type_enum = sa.Enum(
        "suggestions_generated",
        "coverage_drop",
        "suggestion_reviewed",
        "requirement_created",
        "test_case_created",
        name="notificationtype",
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "notifications",
        sa.Column(
            "type",
            sa.Enum(
                "suggestions_generated",
                "coverage_drop",
                "suggestion_reviewed",
                "requirement_created",
                "test_case_created",
                name="notificationtype",
                create_type=False,
            ),
            nullable=False,
            server_default="requirement_created",
        ),
    )
    op.add_column(
        "notifications",
        sa.Column("title", sa.String(255), nullable=False, server_default=""),
    )
    op.add_column(
        "notifications",
        sa.Column("metadata", sa.JSON(), nullable=True),
    )
    # Remove server defaults after adding (they were only needed to populate existing rows)
    op.alter_column("notifications", "type", server_default=None)
    op.alter_column("notifications", "title", server_default=None)


def downgrade() -> None:
    op.drop_column("notifications", "metadata")
    op.drop_column("notifications", "title")
    op.drop_column("notifications", "type")
    sa.Enum(name="notificationtype").drop(op.get_bind(), checkfirst=True)
