"""add actor_kind and actor_token_id to audit_log

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2026-05-07 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i8j9k0l1m2n3"
down_revision: Union[str, None] = "h7i8j9k0l1m2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audit_log", sa.Column("actor_kind", sa.String(length=20), nullable=False, server_default="user"))
    op.add_column("audit_log", sa.Column("actor_token_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.alter_column("audit_log", "user_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)

    op.execute("UPDATE audit_log SET actor_kind = 'user' WHERE actor_kind IS NULL")

    op.create_foreign_key(
        "fk_audit_log_actor_token_id_runner_tokens",
        "audit_log",
        "runner_tokens",
        ["actor_token_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_audit_log_actor_identity",
        "audit_log",
        "(actor_kind = 'user' AND user_id IS NOT NULL AND actor_token_id IS NULL) "
        "OR (actor_kind = 'runner_token' AND actor_token_id IS NOT NULL AND user_id IS NULL)",
    )
    op.create_index("idx_audit_log_actor_token_id", "audit_log", ["actor_token_id"])
    op.create_index("idx_audit_log_actor_kind_created_at", "audit_log", ["actor_kind", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_audit_log_actor_kind_created_at", table_name="audit_log")
    op.drop_index("idx_audit_log_actor_token_id", table_name="audit_log")
    op.drop_constraint("ck_audit_log_actor_identity", "audit_log", type_="check")
    op.drop_constraint("fk_audit_log_actor_token_id_runner_tokens", "audit_log", type_="foreignkey")

    # Restore non-null user_id invariant for pre-actor rows.
    op.execute("DELETE FROM audit_log WHERE user_id IS NULL")
    op.alter_column("audit_log", "user_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    op.drop_column("audit_log", "actor_token_id")
    op.drop_column("audit_log", "actor_kind")
