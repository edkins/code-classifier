"""create project table

Revision ID: 5f789f5689fe
Revises: 3c4d5d2cc2f0
Create Date: 2021-12-11 10:09:21.311743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f789f5689fe'
down_revision = '3c4d5d2cc2f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'project',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code_url', sa.String, nullable=False, unique=True),
        sa.Column('host', sa.String, nullable=True),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('project_url', sa.String, nullable=True),
        sa.Column('doc_url', sa.String, nullable=True),
        sa.Column('public', sa.Boolean, nullable=True),
        sa.Column('is_fork', sa.Boolean, nullable=True),
        sa.Column('git_ssh', sa.String, nullable=True),
        sa.Column('git_https', sa.String, nullable=True),
        sa.Column('language', sa.String, nullable=True),
        sa.Column('size', sa.Integer, nullable=True),
        sa.Column('forks_count', sa.Integer, nullable=True),
        sa.Column('stars_count', sa.Integer, nullable=True),
        sa.Column('main_branch', sa.String, nullable=True),
        sa.Column('create_date', sa.String, nullable=True),
        sa.Column('update_date', sa.String, nullable=True),
        sa.Column('metadata_date', sa.String, nullable=True),
        sa.Column('fetch_date', sa.String, nullable=True),
        sa.Column('fetch_sha', sa.String, nullable=True),
        sa.Column('fetch_location', sa.String, nullable=True)
    )


def downgrade():
    op.drop_table('project')
