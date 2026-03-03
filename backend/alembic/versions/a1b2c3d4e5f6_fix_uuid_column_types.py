"""fix uuid column types for users, audit_log, and notifications tables

Revision ID: a1b2c3d4e5f6
Revises: d3e4f5a6b7c8
Create Date: 2026-03-03 16:00:00.000000
"""

from typing import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "d3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── users table ──────────────────────────────────────────────
    # Drop FKs that reference users.id first
    op.drop_constraint("audit_log_user_id_fkey", "audit_log", type_="foreignkey")
    op.drop_constraint("notifications_user_id_fkey", "notifications", type_="foreignkey")

    # Convert users.id from CHAR(36) to UUID
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE uuid USING id::uuid")

    # ── audit_log table ──────────────────────────────────────────
    op.execute("ALTER TABLE audit_log ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE audit_log ALTER COLUMN user_id TYPE uuid USING user_id::uuid")
    op.execute("ALTER TABLE audit_log ALTER COLUMN resource_id TYPE uuid USING resource_id::uuid")

    # ── notifications table ──────────────────────────────────────
    op.execute("ALTER TABLE notifications ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE notifications ALTER COLUMN user_id TYPE uuid USING user_id::uuid")

    # Recreate the foreign keys
    op.create_foreign_key("audit_log_user_id_fkey", "audit_log", "users", ["user_id"], ["id"])
    op.create_foreign_key(
        "notifications_user_id_fkey", "notifications", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    # Drop FKs
    op.drop_constraint("audit_log_user_id_fkey", "audit_log", type_="foreignkey")
    op.drop_constraint("notifications_user_id_fkey", "notifications", type_="foreignkey")

    # Revert UUID columns back to CHAR(36) / VARCHAR(36)
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE char(36) USING id::text")
    op.execute("ALTER TABLE audit_log ALTER COLUMN id TYPE char(36) USING id::text")
    op.execute("ALTER TABLE audit_log ALTER COLUMN user_id TYPE char(36) USING user_id::text")
    op.execute("ALTER TABLE audit_log ALTER COLUMN resource_id TYPE varchar(36) USING resource_id::text")
    op.execute("ALTER TABLE notifications ALTER COLUMN id TYPE varchar(36) USING id::text")
    op.execute("ALTER TABLE notifications ALTER COLUMN user_id TYPE varchar(36) USING user_id::text")

    # Recreate FKs
    op.create_foreign_key("audit_log_user_id_fkey", "audit_log", "users", ["user_id"], ["id"])
    op.create_foreign_key(
        "notifications_user_id_fkey", "notifications", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
