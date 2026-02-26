"""add performance indexes

Revision ID: d3e4f5a6b7c8
Revises: e4f5a6b7c8d9
Create Date: 2026-02-23 03:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Composite index for duplicate checking in suggestion engine
    op.create_index(
        "idx_suggestions_req_tc",
        "link_suggestions",
        ["requirement_id", "test_case_id"],
    )
    # Index on similarity_score for filtered queries
    op.create_index(
        "idx_suggestions_similarity_score",
        "link_suggestions",
        ["similarity_score"],
    )
    # Index on suggestion_method for algorithm filtering
    op.create_index(
        "idx_suggestions_method",
        "link_suggestions",
        ["suggestion_method"],
    )
    # Composite index for common query pattern (status + score)
    op.create_index(
        "idx_suggestions_status_score",
        "link_suggestions",
        ["status", "similarity_score"],
    )
    # Index on notifications for user + read status
    op.create_index(
        "idx_notifications_user_read",
        "notifications",
        ["user_id", "read"],
    )

def downgrade() -> None:
    op.drop_index("idx_notifications_user_read", table_name="notifications")
    op.drop_index("idx_suggestions_status_score", table_name="link_suggestions")
    op.drop_index("idx_suggestions_method", table_name="link_suggestions")
    op.drop_index("idx_suggestions_similarity_score", table_name="link_suggestions")
    op.drop_index("idx_suggestions_req_tc", table_name="link_suggestions")
