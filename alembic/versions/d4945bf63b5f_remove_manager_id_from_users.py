"""remove manager_id from users

Revision ID: d4945bf63b5f
Revises: f9aa07a173e0
Create Date: 2025-09-15 17:42:21.698751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4945bf63b5f'
down_revision: Union[str, Sequence[str], None] = 'f9aa07a173e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
