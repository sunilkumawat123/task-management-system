"""remove manager_id from users

Revision ID: <your_revision_id>
Revises: <previous_revision_id>
Create Date: 2025-09-15
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '<your_revision_id>'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop manager_id column from users
    op.drop_constraint('users_manager_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'manager_id')

def downgrade() -> None:
    # Recreate manager_id column if downgrading
    op.add_column('users', sa.Column('manager_id', sa.Integer(), nullable=True))
    op.create_foreign_key('users_manager_id_fkey', 'users', 'users', ['manager_id'], ['id'])
