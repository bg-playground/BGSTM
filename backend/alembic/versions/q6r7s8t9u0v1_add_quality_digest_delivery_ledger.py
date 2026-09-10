"""add quality digest delivery ledger

Revision ID: q6r7s8t9u0v1
Revises: p5q6r7s8t9u0
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "q6r7s8t9u0v1"
down_revision: Union[str, None] = "p5q6r7s8t9u0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _guid_type(bind):
    if bind.dialect.name == "postgresql":
        return postgresql.UUID(as_uuid=True)
    return sa.String(length=36)


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if "quality_digest_deliveries" in insp.get_table_names():
        return

    guid = _guid_type(bind)
    op.create_table(
        "quality_digest_deliveries",
        sa.Column("id", guid, nullable=False),
        sa.Column(
            "subscription_id",
            _guid_type(bind),
            sa.ForeignKey("quality_digest_subscriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(), nullable=False),
        sa.Column(
            "notification_id",
            _guid_type(bind),
            sa.ForeignKey("notifications.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subscription_id",
            "due_at",
            name="uq_quality_digest_delivery_subscription_due",
        ),
    )
    op.create_index(
        "ix_quality_digest_deliveries_subscription_id",
        "quality_digest_deliveries",
        ["subscription_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if "quality_digest_deliveries" in insp.get_table_names():
        op.drop_index(
            "ix_quality_digest_deliveries_subscription_id",
            table_name="quality_digest_deliveries",
        )
        op.drop_table("quality_digest_deliveries")
