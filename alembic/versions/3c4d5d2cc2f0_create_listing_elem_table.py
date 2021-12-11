"""create listing_elem table

Revision ID: 3c4d5d2cc2f0
Revises: 9db7c41f405d
Create Date: 2021-12-11 09:51:55.350109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c4d5d2cc2f0'
down_revision = '9db7c41f405d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'listing_elem',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('listing_id', sa.Integer, nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('url', sa.String, nullable=True)
    )


def downgrade():
    op.drop_table('listing_elem')
