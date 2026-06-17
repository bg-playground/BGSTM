"""add release signoffs table

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-06-17 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "o4p5q6r7s8t9"
down_revision: Union[str, None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    if "release_signoffs" in insp.get_table_names():
        return

    role_enum = sa.Enum("qa_lead", "product", "eng_lead", name="releasesignoffrole")
    role_enum.create(bind, checkfirst=True)

    op.create_table(
        "release_signoffs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.Enum("qa_lead", "product", "eng_lead", name="releasesignoffrole", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "signed_off_by_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("signed_off_at", sa.DateTime(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_release_signoffs_role", "release_signoffs", ["role"], unique=False)
    op.create_index("idx_release_signoffs_revoked_at", "release_signoffs", ["revoked_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    if "release_signoffs" in insp.get_table_names():
        existing_indexes = {idx["name"] for idx in insp.get_indexes("release_signoffs")}
        if "idx_release_signoffs_role" in existing_indexes:
            op.drop_index("idx_release_signoffs_role", table_name="release_signoffs")
        if "idx_release_signoffs_revoked_at" in existing_indexes:
            op.drop_index("idx_release_signoffs_revoked_at", table_name="release_signoffs")
        op.drop_table("release_signoffs")

    sa.Enum(name="releasesignoffrole").drop(bind, checkfirst=True)
