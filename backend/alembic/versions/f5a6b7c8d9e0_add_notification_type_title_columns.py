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


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    existing_columns = {c["name"] for c in insp.get_columns("notifications")}

    notification_type_enum = sa.Enum(
        "suggestions_generated",
        "coverage_drop",
        "suggestion_reviewed",
        "requirement_created",
        "test_case_created",
        name="notificationtype",
    )
    notification_type_enum.create(bind, checkfirst=True)

    if "type" not in existing_columns:
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

    if "title" not in existing_columns:
        op.add_column(
            "notifications",
            sa.Column("title", sa.String(255), nullable=False, server_default=""),
        )
        op.alter_column("notifications", "title", server_default=None)

    if "metadata" not in existing_columns:
        op.add_column(
            "notifications",
            sa.Column("metadata", sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    existing_columns = {c["name"] for c in insp.get_columns("notifications")}

    if "metadata" in existing_columns:
        op.drop_column("notifications", "metadata")
    if "title" in existing_columns:
        op.drop_column("notifications", "title")
    if "type" in existing_columns:
        op.drop_column("notifications", "type")
    sa.Enum(name="notificationtype").drop(bind, checkfirst=True)
