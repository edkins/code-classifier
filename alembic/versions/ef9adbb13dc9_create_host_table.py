"""create host table

Revision ID: ef9adbb13dc9
Revises: 5f789f5689fe
Create Date: 2021-12-12 14:58:01.873008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef9adbb13dc9'
down_revision = '5f789f5689fe'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'host',
        sa.Column('host', sa.String, nullable=False, unique=True),
        sa.Column('requests_per_hour', sa.Integer, nullable=False),
        sa.Column('fetch_date', sa.String, nullable=True),
        sa.Column('requests_remaining', sa.Integer, nullable=True)
    )

def downgrade():
    op.drop_table('host')
