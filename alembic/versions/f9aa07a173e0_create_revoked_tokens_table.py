"""create revoked_tokens table

Revision ID: f9aa07a173e0
Revises: d905b9eb50c1
Create Date: 2025-09-15 16:47:12.614943
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'f9aa07a173e0'
down_revision = 'd905b9eb50c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create revoked_tokens table."""
    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('token', sa.String, unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )


def downgrade() -> None:
    """Drop revoked_tokens table."""
    op.drop_table('revoked_tokens')
