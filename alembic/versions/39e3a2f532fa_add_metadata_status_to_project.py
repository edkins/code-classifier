"""add metadata_status to project

Revision ID: 39e3a2f532fa
Revises: ef9adbb13dc9
Create Date: 2021-12-12 16:56:57.830398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39e3a2f532fa'
down_revision = 'ef9adbb13dc9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('metadata_status', sa.Integer, nullable=True))
    op.execute("UPDATE project SET metadata_status=200 WHERE metadata_status is null AND metadata_date is not null")

def downgrade():
    op.drop_column('project', 'metadata_status')
