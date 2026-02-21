"""initial schema

Revision ID: a61ce9bc5970
Revises:
Create Date: 2026-02-21 04:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a61ce9bc5970"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    requirement_type = sa.Enum("functional", "non_functional", "technical", name="requirementtype")
    priority_level = sa.Enum("critical", "high", "medium", "low", name="prioritylevel")
    requirement_status = sa.Enum("draft", "approved", "implemented", "tested", "closed", name="requirementstatus")
    test_case_type = sa.Enum(
        "functional", "integration", "performance", "security", "ui", "regression", name="testcasetype"
    )
    test_case_status = sa.Enum(
        "draft", "ready", "executing", "passed", "failed", "blocked", "deprecated", name="testcasestatus"
    )
    automation_status = sa.Enum("manual", "automated", "automatable", name="automationstatus")
    link_type = sa.Enum("covers", "verifies", "validates", "related", name="linktype")
    link_source = sa.Enum("manual", "ai_suggested", "ai_confirmed", "imported", name="linksource")
    suggestion_method = sa.Enum(
        "semantic_similarity", "keyword_match", "heuristic", "hybrid", "llm_embedding", name="suggestionmethod"
    )
    suggestion_status = sa.Enum("pending", "accepted", "rejected", "expired", name="suggestionstatus")

    op.create_table(
        "requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(100), nullable=True, unique=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", requirement_type, nullable=False),
        sa.Column("priority", priority_level, nullable=False),
        sa.Column("status", requirement_status, nullable=False, server_default="draft"),
        sa.Column("module", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("custom_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("source_system", sa.String(50), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_requirements_external_id", "requirements", ["external_id"])
    op.create_index("idx_requirements_title", "requirements", ["title"])
    op.create_index("idx_requirements_status", "requirements", ["status"])
    op.create_index("idx_requirements_module", "requirements", ["module"])

    op.create_table(
        "test_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(100), nullable=True, unique=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", test_case_type, nullable=False),
        sa.Column("priority", priority_level, nullable=False),
        sa.Column("status", test_case_status, nullable=False, server_default="draft"),
        sa.Column("steps", postgresql.JSONB(), nullable=True),
        sa.Column("preconditions", sa.Text(), nullable=True),
        sa.Column("postconditions", sa.Text(), nullable=True),
        sa.Column("test_data", postgresql.JSONB(), nullable=True),
        sa.Column("module", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("automation_status", automation_status, nullable=True),
        sa.Column("execution_time_minutes", sa.Integer(), nullable=True),
        sa.Column("custom_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("source_system", sa.String(50), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_test_cases_external_id", "test_cases", ["external_id"])
    op.create_index("idx_test_cases_title", "test_cases", ["title"])
    op.create_index("idx_test_cases_status", "test_cases", ["status"])
    op.create_index("idx_test_cases_module", "test_cases", ["module"])

    op.create_table(
        "requirement_test_case_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "requirement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("requirements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("test_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("link_type", link_type, nullable=False, server_default="covers"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("link_source", link_source, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_by", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("requirement_id", "test_case_id", name="uq_requirement_test_case"),
    )
    op.create_index("idx_links_requirement_id", "requirement_test_case_links", ["requirement_id"])
    op.create_index("idx_links_test_case_id", "requirement_test_case_links", ["test_case_id"])

    op.create_table(
        "link_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "requirement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("requirements.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("test_cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("suggestion_method", suggestion_method, nullable=False),
        sa.Column("suggestion_reason", sa.Text(), nullable=True),
        sa.Column("suggestion_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("status", suggestion_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("reviewed_by", sa.String(100), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
    )
    op.create_index("idx_suggestions_requirement_id", "link_suggestions", ["requirement_id"])
    op.create_index("idx_suggestions_test_case_id", "link_suggestions", ["test_case_id"])
    op.create_index("idx_suggestions_status", "link_suggestions", ["status"])


def downgrade() -> None:
    op.drop_index("idx_suggestions_status", table_name="link_suggestions")
    op.drop_index("idx_suggestions_test_case_id", table_name="link_suggestions")
    op.drop_index("idx_suggestions_requirement_id", table_name="link_suggestions")
    op.drop_table("link_suggestions")

    op.drop_index("idx_links_test_case_id", table_name="requirement_test_case_links")
    op.drop_index("idx_links_requirement_id", table_name="requirement_test_case_links")
    op.drop_table("requirement_test_case_links")

    op.drop_index("idx_test_cases_module", table_name="test_cases")
    op.drop_index("idx_test_cases_status", table_name="test_cases")
    op.drop_index("idx_test_cases_title", table_name="test_cases")
    op.drop_index("idx_test_cases_external_id", table_name="test_cases")
    op.drop_table("test_cases")

    op.drop_index("idx_requirements_module", table_name="requirements")
    op.drop_index("idx_requirements_status", table_name="requirements")
    op.drop_index("idx_requirements_title", table_name="requirements")
    op.drop_index("idx_requirements_external_id", table_name="requirements")
    op.drop_table("requirements")

    sa.Enum(name="suggestionstatus").drop(op.get_bind())
    sa.Enum(name="suggestionmethod").drop(op.get_bind())
    sa.Enum(name="linksource").drop(op.get_bind())
    sa.Enum(name="linktype").drop(op.get_bind())
    sa.Enum(name="automationstatus").drop(op.get_bind())
    sa.Enum(name="testcasestatus").drop(op.get_bind())
    sa.Enum(name="testcasetype").drop(op.get_bind())
    sa.Enum(name="requirementstatus").drop(op.get_bind())
    sa.Enum(name="prioritylevel").drop(op.get_bind())
    sa.Enum(name="requirementtype").drop(op.get_bind())
