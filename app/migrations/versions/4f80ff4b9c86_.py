"""Adds public identifier column

Revision ID: 4f80ff4b9c86
Revises: 50884930bc8e
Create Date: 2020-04-03 19:47:49.851926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f80ff4b9c86'
down_revision = '50884930bc8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organizations', sa.Column('public_identifier', sa.String(length=8), nullable=False))
    op.create_index(op.f('ix_organizations_public_identifier'), 'organizations', ['public_identifier'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_organizations_public_identifier'), table_name='organizations')
    op.drop_column('organizations', 'public_identifier')
    # ### end Alembic commands ###
