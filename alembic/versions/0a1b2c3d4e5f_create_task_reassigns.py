"""create task_reassigns table

Revision ID: 0a1b2c3d4e5f
Revises: f9aa07a173e0
Create Date: 2025-09-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0a1b2c3d4e5f'
down_revision = 'f9aa07a173e0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'task_reassigns',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id'), nullable=True),
        sa.Column('previous_assignee_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('new_assignee_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reassigned_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reason', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table('task_reassigns')
