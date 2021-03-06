"""Adds roles table

Revision ID: 3060146b5c99
Revises: 5546a634cce0
Create Date: 2020-05-13 23:45:29.363602

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3060146b5c99"
down_revision = "5546a634cce0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("roles")
    # ### end Alembic commands ###
