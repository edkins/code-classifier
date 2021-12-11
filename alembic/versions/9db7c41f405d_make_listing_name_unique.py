"""make listing name unique

Revision ID: 9db7c41f405d
Revises: fba9f55b9aef
Create Date: 2021-12-10 21:00:53.325922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9db7c41f405d'
down_revision = 'fba9f55b9aef'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('listing') as batch_op:
        batch_op.create_unique_constraint('unique_name', ['name'])


def downgrade():
    with op.batch_alter_table('listing') as batch_op:
        batch_op.drop_constraint('unique_name')
