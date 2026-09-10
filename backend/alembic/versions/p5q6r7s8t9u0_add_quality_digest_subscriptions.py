"""add quality digest subscriptions

Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "p5q6r7s8t9u0"
down_revision: Union[str, None] = "o4p5q6r7s8t9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'quality_digest'")

    insp = inspect(bind)
    if "quality_digest_subscriptions" in insp.get_table_names():
        return

    op.create_table(
        "quality_digest_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.Enum("in_app", name="digestchannel"), nullable=False),
        sa.Column("cadence", sa.Enum("off", "daily", "weekly", name="digestcadence"), nullable=False),
        sa.Column("window_days", sa.Integer(), nullable=False),
        sa.Column("last_delivered_at", sa.DateTime(), nullable=True),
        sa.Column("next_delivery_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "channel", name="uq_quality_digest_user_channel"),
    )
    op.create_index("ix_quality_digest_subscriptions_user_id", "quality_digest_subscriptions", ["user_id"])
    op.create_index("ix_quality_digest_subscriptions_next_delivery_at", "quality_digest_subscriptions", ["next_delivery_at"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if "quality_digest_subscriptions" in insp.get_table_names():
        op.drop_index("ix_quality_digest_subscriptions_next_delivery_at", table_name="quality_digest_subscriptions")
        op.drop_index("ix_quality_digest_subscriptions_user_id", table_name="quality_digest_subscriptions")
        op.drop_table("quality_digest_subscriptions")
    sa.Enum(name="digestcadence").drop(bind, checkfirst=True)
    sa.Enum(name="digestchannel").drop(bind, checkfirst=True)
    # PostgreSQL enum values cannot be safely removed without rebuilding the type.
