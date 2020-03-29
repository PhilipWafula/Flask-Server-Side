"""Adds domain to organization configurations

Revision ID: 34d54c413880
Revises: fab4b86ff429
Create Date: 2020-03-29 23:09:54.518285

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34d54c413880'
down_revision = 'fab4b86ff429'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('configurations', sa.Column('domain', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('configurations', 'domain')
    # ### end Alembic commands ###
