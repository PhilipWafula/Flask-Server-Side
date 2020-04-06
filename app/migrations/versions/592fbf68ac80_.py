"""Makes msisdn nullable for creation admin users.

Revision ID: 592fbf68ac80
Revises: 333494146438
Create Date: 2020-04-01 13:56:52.333355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '592fbf68ac80'
down_revision = '333494146438'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'msisdn',
               existing_type=sa.VARCHAR(length=13),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'msisdn',
               existing_type=sa.VARCHAR(length=13),
               nullable=False)
    # ### end Alembic commands ###
