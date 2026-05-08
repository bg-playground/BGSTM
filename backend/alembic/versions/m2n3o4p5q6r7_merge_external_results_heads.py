"""merge external-results migration heads

Revision ID: m2n3o4p5q6r7
Revises: j9k0l1m2n3o4, l1m2n3o4p5q6
Create Date: 2026-05-08 17:58:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "m2n3o4p5q6r7"
down_revision: str | Sequence[str] | None = ("j9k0l1m2n3o4", "l1m2n3o4p5q6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
