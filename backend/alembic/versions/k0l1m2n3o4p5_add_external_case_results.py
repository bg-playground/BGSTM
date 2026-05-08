"""add external_case_results table

Revision ID: k0l1m2n3o4p5
Revises: i8j9k0l1m2n3
Create Date: 2026-05-08 12:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "k0l1m2n3o4p5"
down_revision: Union[str, None] = "i8j9k0l1m2n3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    columns = inspect(bind).get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        case_outcome_enum = postgresql.ENUM(
            "started",
            "passed",
            "failed",
            "skipped",
            "flaky",
            "aborted",
            name="case_outcome",
        )
        case_outcome_enum.create(op.get_bind(), checkfirst=True)
    else:
        case_outcome_enum = sa.Enum("started", "passed", "failed", "skipped", "flaky", "aborted", name="case_outcome")

    op.create_table(
        "external_case_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("external_run_sessions.id", name="fk_external_case_results_session_id"),
            nullable=False,
        ),
        sa.Column(
            "test_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("test_cases.id", name="fk_external_case_results_test_case_id"),
            nullable=True,
        ),
        sa.Column("external_id", sa.String(length=500), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("outcome", case_outcome_enum, nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("auto_registered", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("duration_ms >= 0", name="ck_external_case_results_duration_ms_nonnegative"),
    )
    op.create_index("idx_external_case_results_session_id", "external_case_results", ["session_id"])
    op.create_index(
        "uq_external_case_results_session_external_id",
        "external_case_results",
        ["session_id", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    if not _has_column("test_cases", "auto_registered"):
        op.add_column(
            "test_cases",
            sa.Column("auto_registered", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    if _has_column("test_cases", "auto_registered"):
        op.drop_column("test_cases", "auto_registered")

    op.drop_index("uq_external_case_results_session_external_id", table_name="external_case_results")
    op.drop_index("idx_external_case_results_session_id", table_name="external_case_results")
    op.drop_table("external_case_results")

    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS case_outcome")
