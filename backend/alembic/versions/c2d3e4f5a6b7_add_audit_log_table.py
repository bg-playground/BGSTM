"""add audit_log table

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-02-22 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("user_id", sa.CHAR(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("idx_audit_log_action", "audit_log", ["action"])
    op.create_index("idx_audit_log_resource_type", "audit_log", ["resource_type"])


def downgrade() -> None:
    op.drop_index("idx_audit_log_resource_type", table_name="audit_log")
    op.drop_index("idx_audit_log_action", table_name="audit_log")
    op.drop_index("idx_audit_log_user_id", table_name="audit_log")
    op.drop_table("audit_log")
