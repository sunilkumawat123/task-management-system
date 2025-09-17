"""merge heads

Revision ID: b5ce118d507e
Revises: 0a1b2c3d4e5f, d4945bf63b5f
Create Date: 2025-09-16 18:07:48.967116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5ce118d507e'
down_revision: Union[str, Sequence[str], None] = ('0a1b2c3d4e5f', 'd4945bf63b5f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
