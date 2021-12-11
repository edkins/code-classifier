"""create listing table

Revision ID: fba9f55b9aef
Revises: 
Create Date: 2021-12-10 19:48:22.316989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fba9f55b9aef'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'listing',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('url', sa.String, nullable=True)
    )


def downgrade():
    op.drop_table('listing')
