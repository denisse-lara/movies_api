"""user and jwt models

Revision ID: c14aaa9f0b8f
Revises: 
Create Date: 2022-03-15 21:07:48.508218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c14aaa9f0b8f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "jwt_whitelist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "user_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.String(length=50), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=150), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("banned", sa.Boolean(), nullable=False),
        sa.Column("admin", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
        sa.UniqueConstraint("username"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_profile")
    op.drop_table("jwt_whitelist")
    # ### end Alembic commands ###
