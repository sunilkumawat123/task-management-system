"""add uuid and created_by_id to users table"""

from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = 'd905b9eb50c1'
down_revision = '97a5210cf716'
branch_labels = None
depends_on = None


def upgrade():
    # Add UUID column with a default value for existing rows
    op.add_column(
        'users',
        sa.Column('uuid', sa.String(), nullable=False, server_default=str(uuid.uuid4()))
    )

    # Add created_by_id column (self-referencing foreign key)
    op.add_column(
        'users',
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True)
    )


def downgrade():
    op.drop_column('users', 'created_by_id')
    op.drop_column('users', 'uuid')
