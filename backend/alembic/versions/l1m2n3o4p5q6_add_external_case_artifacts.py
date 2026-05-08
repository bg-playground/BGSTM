"""add external_case_artifacts table

Revision ID: l1m2n3o4p5q6
Revises: k0l1m2n3o4p5
Create Date: 2026-05-08 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "l1m2n3o4p5q6"
down_revision: Union[str, None] = "k0l1m2n3o4p5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        artifact_kind_enum = postgresql.ENUM(
            "screenshot",
            "video",
            "trace",
            "log",
            "other",
            name="artifact_kind",
            create_type=False,
        )
        artifact_kind_enum.create(op.get_bind(), checkfirst=True)
    else:
        artifact_kind_enum = sa.Enum("screenshot", "video", "trace", "log", "other", name="artifact_kind")

    op.create_table(
        "external_case_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "case_result_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "external_case_results.id",
                ondelete="CASCADE",
                name="fk_external_case_artifacts_case_result_id",
            ),
            nullable=False,
        ),
        sa.Column("kind", artifact_kind_enum, nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=200), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(length=1000), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "idx_external_case_artifacts_case_result_id",
        "external_case_artifacts",
        ["case_result_id"],
    )


def downgrade() -> None:
    op.drop_index("idx_external_case_artifacts_case_result_id", table_name="external_case_artifacts")
    op.drop_table("external_case_artifacts")

    if op.get_bind().dialect.name == "postgresql":
        artifact_kind_enum = postgresql.ENUM(
            "screenshot",
            "video",
            "trace",
            "log",
            "other",
            name="artifact_kind",
            create_type=False,
        )
        artifact_kind_enum.drop(op.get_bind(), checkfirst=True)
