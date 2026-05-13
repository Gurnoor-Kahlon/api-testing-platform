"""initial tables

Revision ID: 0001_initial_tables
Revises: 
Create Date: 2026-05-13
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("tasks", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(length=100), nullable=False), sa.Column("description", sa.String(length=300), nullable=False), sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.create_table("test_runs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("test_name", sa.String(length=100), nullable=False), sa.Column("test_type", sa.String(length=20), nullable=False), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("result", sa.String(length=1000)), sa.Column("execution_time", sa.Float()), sa.Column("created_at", sa.DateTime()))
    op.create_table("test_sessions", sa.Column("id", sa.String(length=100), primary_key=True), sa.Column("status", sa.String(length=50), nullable=False), sa.Column("started_at", sa.DateTime()), sa.Column("finished_at", sa.DateTime()), sa.Column("return_code", sa.Integer()), sa.Column("stdout", sa.String(length=5000)), sa.Column("stderr", sa.String(length=5000)))

def downgrade() -> None:
    op.drop_table("test_sessions")
    op.drop_table("test_runs")
    op.drop_table("tasks")
