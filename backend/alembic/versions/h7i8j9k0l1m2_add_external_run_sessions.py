"""add external_run_sessions table

Revision ID: h7i8j9k0l1m2
Revises: g6h7i8j9k0l1
Create Date: 2026-05-06 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h7i8j9k0l1m2"
down_revision: Union[str, None] = "g6h7i8j9k0l1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_run_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("runner", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("started", "passed", "failed", "skipped", "aborted", name="runstatus"),
            nullable=False,
            server_default="started",
        ),
        sa.Column("git_sha", sa.String(255), nullable=True),
        sa.Column("git_branch", sa.String(255), nullable=True),
        sa.Column("ci_url", sa.String(2048), nullable=True),
        sa.Column("run_metadata", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column(
            "created_by_runner_token_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("runner_tokens.id"),
            nullable=False,
        ),
    )
    op.create_index("idx_external_run_sessions_project_id", "external_run_sessions", ["project_id"])
    op.create_index(
        "idx_external_run_sessions_runner_token_id",
        "external_run_sessions",
        ["created_by_runner_token_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_external_run_sessions_runner_token_id", table_name="external_run_sessions")
    op.drop_index("idx_external_run_sessions_project_id", table_name="external_run_sessions")
    op.drop_table("external_run_sessions")
    # Drop the enum type on PostgreSQL (no-op on other dialects).
    op.execute("DROP TYPE IF EXISTS runstatus")
