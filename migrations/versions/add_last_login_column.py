"""Add last_login column to users table

Revision ID: add_last_login_column
Revises: 
Create Date: 2023-09-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_last_login_column'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the last_login column to the users table
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))


def downgrade():
    # Remove the last_login column
    op.drop_column('users', 'last_login')