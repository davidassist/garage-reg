"""add_missing_dynamic_checklist_fields

Revision ID: 177019ee0ca0
Revises: 5e606b96d84d
Create Date: 2025-10-02 05:39:15.134518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '177019ee0ca0'
down_revision: Union[str, Sequence[str], None] = 'a7486a6e8cfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing column to checklist_items
    with op.batch_alter_table('checklist_items', schema=None) as batch_op:
        # Add missing conditional_rules column
        batch_op.add_column(sa.Column('conditional_rules', sa.JSON(), nullable=True))
        
        # Create foreign key constraint for depends_on_item_id
        batch_op.create_foreign_key('fk_depends_on_item', 'checklist_items', ['depends_on_item_id'], ['id'])
        
        # Add indexes for new fields
        batch_op.create_index('ix_checklist_items_section', ['section'])
        batch_op.create_index('ix_checklist_items_measurement_type', ['measurement_type'])
        batch_op.create_index('ix_checklist_items_depends_on', ['depends_on_item_id'])
        batch_op.create_index('ix_checklist_items_is_recommended', ['is_recommended'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('checklist_items', schema=None) as batch_op:
        # Remove indexes
        batch_op.drop_index('ix_checklist_items_is_recommended')
        batch_op.drop_index('ix_checklist_items_depends_on')
        batch_op.drop_index('ix_checklist_items_measurement_type')
        batch_op.drop_index('ix_checklist_items_section')
        
        # Remove foreign key constraint
        batch_op.drop_constraint('fk_depends_on_item', type_='foreignkey')
        
        # Remove column
        batch_op.drop_column('conditional_rules')
