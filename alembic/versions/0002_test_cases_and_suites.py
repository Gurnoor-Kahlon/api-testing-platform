"""add api test cases and suites

Revision ID: 0002_test_cases_and_suites
Revises: 0001_initial_tables
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_test_cases_and_suites"
down_revision = "0001_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("http_method", sa.String(length=10), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("headers", sa.JSON(), nullable=True),
        sa.Column("query_params", sa.JSON(), nullable=True),
        sa.Column("request_body", sa.JSON(), nullable=True),
        sa.Column("expected_status_code", sa.Integer(), nullable=False),
        sa.Column("expected_response_time_ms", sa.Integer(), nullable=False),
        sa.Column("expected_json_field", sa.String(length=255), nullable=True),
        sa.Column("expected_json_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_api_test_cases_id"), "api_test_cases", ["id"], unique=False)
    op.create_index(op.f("ix_api_test_cases_project_id"), "api_test_cases", ["project_id"], unique=False)

    op.create_table(
        "test_suites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_test_suites_id"), "test_suites", ["id"], unique=False)
    op.create_index(op.f("ix_test_suites_project_id"), "test_suites", ["project_id"], unique=False)

    op.create_table(
        "test_suite_cases",
        sa.Column("suite_id", sa.Integer(), nullable=False),
        sa.Column("test_case_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["suite_id"], ["test_suites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["test_case_id"], ["api_test_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("suite_id", "test_case_id"),
    )


def downgrade() -> None:
    op.drop_table("test_suite_cases")
    op.drop_index(op.f("ix_test_suites_project_id"), table_name="test_suites")
    op.drop_index(op.f("ix_test_suites_id"), table_name="test_suites")
    op.drop_table("test_suites")
    op.drop_index(op.f("ix_api_test_cases_project_id"), table_name="api_test_cases")
    op.drop_index(op.f("ix_api_test_cases_id"), table_name="api_test_cases")
    op.drop_table("api_test_cases")
