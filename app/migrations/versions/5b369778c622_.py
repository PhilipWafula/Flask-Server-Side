"""Creates relationship between users and roles.

Revision ID: 5b369778c622
Revises: 3060146b5c99
Create Date: 2020-05-16 04:09:13.672487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b369778c622'
down_revision = '3060146b5c99'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'role_id')
    # ### end Alembic commands ###
