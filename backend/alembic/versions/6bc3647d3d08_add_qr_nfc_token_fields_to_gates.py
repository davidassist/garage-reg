"""Add QR/NFC token fields to gates

Revision ID: 6bc3647d3d08
Revises: abfec71666fd
Create Date: 2025-10-01 20:35:27.747276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bc3647d3d08'
down_revision: Union[str, Sequence[str], None] = 'abfec71666fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add token_version column
    op.add_column('gates', sa.Column('token_version', sa.Integer, nullable=False, server_default='1'))
    
    # Add last_token_rotation column
    op.add_column('gates', sa.Column('last_token_rotation', sa.DateTime, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove token fields
    op.drop_column('gates', 'last_token_rotation')
    op.drop_column('gates', 'token_version')
