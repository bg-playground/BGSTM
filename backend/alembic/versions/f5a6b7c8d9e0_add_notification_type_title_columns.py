"""add type and title columns to notifications table

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-02-26 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "f5a6b7c8d9e0"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return column in [c["name"] for c in insp.get_columns(table)]


def upgrade() -> None:
    bind = op.get_bind()

    # Create the enum type if it doesn't already exist (idempotent)
    notification_type_enum = sa.Enum(
        "suggestions_generated",
        "coverage_drop",
        "suggestion_reviewed",
        "requirement_created",
        "test_case_created",
        name="notificationtype",
    )
    notification_type_enum.create(bind, checkfirst=True)

    # Only add columns that don't already exist (handles both fresh and pre-existing DBs)
    if not _column_exists("notifications", "type"):
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
        op.alter_column("notifications", "type", server_default=None)

    if not _column_exists("notifications", "title"):
        op.add_column(
            "notifications",
            sa.Column("title", sa.String(255), nullable=False, server_default=""),
        )
        op.alter_column("notifications", "title", server_default=None)

    if not _column_exists("notifications", "metadata"):
        op.add_column(
            "notifications",
            sa.Column("metadata", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    if _column_exists("notifications", "metadata"):
        op.drop_column("notifications", "metadata")
    if _column_exists("notifications", "title"):
        op.drop_column("notifications", "title")
    if _column_exists("notifications", "type"):
        op.drop_column("notifications", "type")
    sa.Enum(name="notificationtype").drop(op.get_bind(), checkfirst=True)
