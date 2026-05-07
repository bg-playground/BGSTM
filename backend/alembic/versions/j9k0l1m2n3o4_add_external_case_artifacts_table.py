"""add external_case_artifacts table

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3
Create Date: 2026-05-07 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "j9k0l1m2n3o4"
down_revision: Union[str, None] = "i8j9k0l1m2n3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_case_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "case_result_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("external_case_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kind",
            sa.Enum("screenshot", "trace", "video", "log", "other", name="artifactkind"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("content_type", sa.String(255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_key", sa.String(1024), nullable=False, unique=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "runner_token_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("runner_tokens.id"),
            nullable=False,
        ),
    )
    op.create_index(
        "idx_external_case_artifacts_case_result_id",
        "external_case_artifacts",
        ["case_result_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_external_case_artifacts_case_result_id", table_name="external_case_artifacts")
    op.drop_table("external_case_artifacts")
    op.execute("DROP TYPE IF EXISTS artifactkind")
