"""add external_case_results table

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2026-05-06 22:50:00.000000

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
    op.add_column("test_cases", sa.Column("auto_registered", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "external_case_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("external_run_sessions.id"),
            nullable=False,
        ),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("test_case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("test_cases.id"), nullable=True),
        sa.Column("external_id", sa.String(length=500), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("outcome", sa.Enum("passed", "failed", "skipped", "flaky", name="caseoutcome"), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_external_case_results_session_id", "external_case_results", ["session_id"])
    op.create_unique_constraint(
        "uq_external_case_results_project_external_id",
        "external_case_results",
        ["project_id", "external_id"],
    )

    op.alter_column("test_cases", "auto_registered", server_default=None)


def downgrade() -> None:
    op.drop_constraint("uq_external_case_results_project_external_id", "external_case_results", type_="unique")
    op.drop_index("idx_external_case_results_session_id", table_name="external_case_results")
    op.drop_table("external_case_results")
    op.execute("DROP TYPE IF EXISTS caseoutcome")
    op.drop_column("test_cases", "auto_registered")
