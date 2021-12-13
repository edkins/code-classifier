"""create wordcount table

Revision ID: 0aa41e240afd
Revises: 39e3a2f532fa
Create Date: 2021-12-12 21:59:59.877628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0aa41e240afd'
down_revision = '39e3a2f532fa'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'wordcount',
        sa.Column('analysis_id', sa.Integer, nullable=False),
        sa.Column('word', sa.String, nullable=False),
        sa.Column('count', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('wordcount')
