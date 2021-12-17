"""add selected to project

Revision ID: fccf77750f44
Revises: 70e4d695dca2
Create Date: 2021-12-14 23:09:55.732858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fccf77750f44'
down_revision = '70e4d695dca2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('selected', sa.Boolean, nullable=True))


def downgrade():
    op.drop_column('project', 'selected')
