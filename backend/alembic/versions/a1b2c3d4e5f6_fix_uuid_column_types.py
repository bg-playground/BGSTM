"""fix uuid column types for users, audit_log, and notifications tables

Revision ID: a1b2c3d4e5f6
Revises: d3e4f5a6b7c8
Create Date: 2026-03-03 16:00:00.000000

NOTE: This migration is now a no-op. The UUID columns are created with the
correct postgresql.UUID type directly in the original migrations:
  - b1c2d3e4f5a6_add_users_table.py
  - c2d3e4f5a6b7_add_audit_log_table.py
  - e4f5a6b7c8d9_add_notifications_table.py
"""

from typing import Sequence

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "d3e4f5a6b7c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
