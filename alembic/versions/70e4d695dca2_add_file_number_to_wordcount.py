"""add file_number to wordcount

Revision ID: 70e4d695dca2
Revises: d3251a19ac54
Create Date: 2021-12-13 18:00:43.226996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70e4d695dca2'
down_revision = 'd3251a19ac54'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('wordcount', sa.Column('file_number', sa.Integer, nullable=True))


def downgrade():
    op.drop_column('wordcount', 'file_number')
