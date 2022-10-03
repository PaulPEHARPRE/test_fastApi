"""init

Revision ID: 1c24ef0fa95a
Revises: 
Create Date: 2022-10-03 09:05:27.211437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c24ef0fa95a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
     op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False)
    )


def downgrade() -> None:
    op.drop_table('users')
