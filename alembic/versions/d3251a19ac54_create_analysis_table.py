"""create analysis table

Revision ID: d3251a19ac54
Revises: 0aa41e240afd
Create Date: 2021-12-12 22:12:37.146658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3251a19ac54'
down_revision = '0aa41e240afd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'analysis',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', sa.Integer, nullable=False)
    )

def downgrade():
    op.drop_table('analysis')
