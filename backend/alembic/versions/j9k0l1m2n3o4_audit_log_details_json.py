"""store audit_log.details as JSONB on PostgreSQL

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3
Create Date: 2026-05-08 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "j9k0l1m2n3o4"
down_revision: Union[str, None] = "i8j9k0l1m2n3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE audit_log
            ALTER COLUMN details TYPE JSONB
            USING CASE
              WHEN details IS NULL OR btrim(details) = '' THEN NULL
              ELSE details::jsonb
            END
            """
        )
        return

    op.alter_column("audit_log", "details", existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE audit_log
            ALTER COLUMN details TYPE TEXT
            USING CASE
              WHEN details IS NULL THEN NULL
              ELSE details::text
            END
            """
        )
        return

    op.alter_column("audit_log", "details", existing_type=sa.JSON(), type_=sa.Text(), existing_nullable=True)
