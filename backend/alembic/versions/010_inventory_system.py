"""Add inventory management with double-entry bookkeeping

Revision ID: 010_inventory_system
Revises: 
Create Date: 2025-10-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_inventory_system'
down_revision = None  # Set this to the last migration
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to existing stock_movements table for double-entry bookkeeping
    op.add_column('stock_movements', sa.Column('movement_number', sa.String(length=50), nullable=True))
    op.add_column('stock_movements', sa.Column('debit_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0'))
    op.add_column('stock_movements', sa.Column('credit_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0'))
    
    # Create unique constraint for movement_number after populating it
    op.execute("UPDATE stock_movements SET movement_number = 'MOV' || to_char(movement_date, 'YYYYMMDD') || lpad(id::text, 4, '0') WHERE movement_number IS NULL")
    op.alter_column('stock_movements', 'movement_number', nullable=False)
    op.create_unique_constraint('uq_stock_movements_movement_number', 'stock_movements', ['movement_number'])
    
    # Update debit/credit quantities based on existing quantity field
    op.execute("""
        UPDATE stock_movements 
        SET debit_quantity = CASE WHEN quantity >= 0 THEN quantity ELSE 0 END,
            credit_quantity = CASE WHEN quantity < 0 THEN ABS(quantity) ELSE 0 END
    """)
    
    # Create stock_alerts table
    op.create_table('stock_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('current_quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('threshold_quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('shortage_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('days_of_stock', sa.Integer(), nullable=True),
        sa.Column('first_detected', sa.DateTime(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('message', sa.String(length=500), nullable=True),
        sa.Column('action_required', sa.String(length=500), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('notifications_sent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_notification_sent', sa.DateTime(), nullable=True),
        sa.Column('estimated_cost_impact', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('business_criticality', sa.String(length=20), nullable=True),
        sa.Column('auto_reorder_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_reorder_triggered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stock_alert_business', 'stock_alerts', ['business_criticality'], unique=False)
    op.create_index('idx_stock_alert_detected', 'stock_alerts', ['first_detected'], unique=False)
    op.create_index('idx_stock_alert_inventory', 'stock_alerts', ['inventory_item_id'], unique=False)
    op.create_index('idx_stock_alert_part', 'stock_alerts', ['part_id'], unique=False)
    op.create_index('idx_stock_alert_priority', 'stock_alerts', ['priority'], unique=False)
    op.create_index('idx_stock_alert_severity', 'stock_alerts', ['severity'], unique=False)
    op.create_index('idx_stock_alert_status', 'stock_alerts', ['status'], unique=False)
    op.create_index('idx_stock_alert_type', 'stock_alerts', ['alert_type'], unique=False)
    op.create_index('idx_stock_alert_warehouse', 'stock_alerts', ['warehouse_id'], unique=False)

    # Create stock_takes table
    op.create_table('stock_takes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('stock_take_number', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('stock_take_type', sa.String(length=20), nullable=False, server_default='full'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='planned'),
        sa.Column('planned_date', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('planned_by', sa.Integer(), nullable=False),
        sa.Column('performed_by', sa.Integer(), nullable=True),
        sa.Column('supervised_by', sa.Integer(), nullable=True),
        sa.Column('items_planned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_counted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_with_variance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('adjustments_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_variance_quantity', sa.Numeric(precision=15, scale=3), nullable=False, server_default='0'),
        sa.Column('total_variance_value', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('variance_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('freeze_movements', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('variance_tolerance', sa.Numeric(precision=5, scale=2), nullable=False, server_default='2.0'),
        sa.Column('require_approval', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['planned_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['supervised_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stock_take_number', 'stock_takes', ['stock_take_number'], unique=True)
    op.create_index('idx_stock_take_planned', 'stock_takes', ['planned_date'], unique=False)
    op.create_index('idx_stock_take_status', 'stock_takes', ['status'], unique=False)
    op.create_index('idx_stock_take_type', 'stock_takes', ['stock_take_type'], unique=False)
    op.create_index('idx_stock_take_warehouse', 'stock_takes', ['warehouse_id'], unique=False)

    # Create stock_take_lines table
    op.create_table('stock_take_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('stock_take_id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('location_code', sa.String(length=50), nullable=True),
        sa.Column('bin_location', sa.String(length=50), nullable=True),
        sa.Column('system_quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('counted_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_quantity', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('variance_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('variance_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_counted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('count_sequence', sa.Integer(), nullable=True),
        sa.Column('counted_at', sa.DateTime(), nullable=True),
        sa.Column('counted_by', sa.Integer(), nullable=True),
        sa.Column('variance_reason', sa.String(length=200), nullable=True),
        sa.Column('variance_category', sa.String(length=50), nullable=True),
        sa.Column('requires_investigation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_adjusted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('adjustment_created', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('stock_movement_id', sa.Integer(), nullable=True),
        sa.Column('count_confidence', sa.String(length=20), nullable=True),
        sa.Column('requires_recount', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recount_reason', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('counting_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['counted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['stock_movement_id'], ['stock_movements.id'], ),
        sa.ForeignKeyConstraint(['stock_take_id'], ['stock_takes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stock_take_line_counted', 'stock_take_lines', ['is_counted'], unique=False)
    op.create_index('idx_stock_take_line_inventory', 'stock_take_lines', ['inventory_item_id'], unique=False)
    op.create_index('idx_stock_take_line_location', 'stock_take_lines', ['location_code'], unique=False)
    op.create_index('idx_stock_take_line_part', 'stock_take_lines', ['part_id'], unique=False)
    op.create_index('idx_stock_take_line_stock_take', 'stock_take_lines', ['stock_take_id'], unique=False)
    op.create_index('idx_stock_take_line_variance', 'stock_take_lines', ['variance_quantity'], unique=False)

    # Add inventory integration columns to part_usages table
    op.add_column('part_usages', sa.Column('inventory_item_id', sa.Integer(), nullable=True))
    op.add_column('part_usages', sa.Column('warehouse_id', sa.Integer(), nullable=True))
    op.add_column('part_usages', sa.Column('stock_movement_id', sa.Integer(), nullable=True))
    op.add_column('part_usages', sa.Column('quantity_issued', sa.Numeric(precision=10, scale=3), nullable=True))
    op.add_column('part_usages', sa.Column('batch_number', sa.String(length=100), nullable=True))
    op.add_column('part_usages', sa.Column('serial_number', sa.String(length=100), nullable=True))
    op.add_column('part_usages', sa.Column('reserved_at', sa.DateTime(), nullable=True))
    op.add_column('part_usages', sa.Column('issued_at', sa.DateTime(), nullable=True))
    op.add_column('part_usages', sa.Column('consumed_at', sa.DateTime(), nullable=True))
    
    # Create foreign key constraints for part_usages
    op.create_foreign_key('fk_part_usages_inventory_item', 'part_usages', 'inventory_items', ['inventory_item_id'], ['id'])
    op.create_foreign_key('fk_part_usages_warehouse', 'part_usages', 'warehouses', ['warehouse_id'], ['id'])
    op.create_foreign_key('fk_part_usages_stock_movement', 'part_usages', 'stock_movements', ['stock_movement_id'], ['id'])
    
    # Create indexes for part_usages
    op.create_index('idx_part_usages_inventory_item', 'part_usages', ['inventory_item_id'], unique=False)
    op.create_index('idx_part_usages_warehouse', 'part_usages', ['warehouse_id'], unique=False)
    op.create_index('idx_part_usages_stock_movement', 'part_usages', ['stock_movement_id'], unique=False)

    # Add check constraints for double-entry bookkeeping
    op.create_check_constraint(
        'check_debit_quantity_positive', 
        'stock_movements', 
        'debit_quantity >= 0'
    )
    op.create_check_constraint(
        'check_credit_quantity_positive', 
        'stock_movements', 
        'credit_quantity >= 0'
    )
    op.create_check_constraint(
        'check_single_entry_per_movement', 
        'stock_movements', 
        '(debit_quantity > 0 AND credit_quantity = 0) OR (debit_quantity = 0 AND credit_quantity > 0)'
    )


def downgrade():
    # Drop new tables
    op.drop_table('stock_take_lines')
    op.drop_table('stock_takes')
    op.drop_table('stock_alerts')
    
    # Remove columns from part_usages
    op.drop_constraint('fk_part_usages_stock_movement', 'part_usages', type_='foreignkey')
    op.drop_constraint('fk_part_usages_warehouse', 'part_usages', type_='foreignkey')
    op.drop_constraint('fk_part_usages_inventory_item', 'part_usages', type_='foreignkey')
    
    op.drop_index('idx_part_usages_stock_movement', 'part_usages')
    op.drop_index('idx_part_usages_warehouse', 'part_usages')
    op.drop_index('idx_part_usages_inventory_item', 'part_usages')
    
    op.drop_column('part_usages', 'consumed_at')
    op.drop_column('part_usages', 'issued_at')
    op.drop_column('part_usages', 'reserved_at')
    op.drop_column('part_usages', 'serial_number')
    op.drop_column('part_usages', 'batch_number')
    op.drop_column('part_usages', 'quantity_issued')
    op.drop_column('part_usages', 'stock_movement_id')
    op.drop_column('part_usages', 'warehouse_id')
    op.drop_column('part_usages', 'inventory_item_id')
    
    # Remove check constraints
    op.drop_constraint('check_single_entry_per_movement', 'stock_movements', type_='check')
    op.drop_constraint('check_credit_quantity_positive', 'stock_movements', type_='check')
    op.drop_constraint('check_debit_quantity_positive', 'stock_movements', type_='check')
    
    # Remove columns from stock_movements
    op.drop_constraint('uq_stock_movements_movement_number', 'stock_movements', type_='unique')
    op.drop_column('stock_movements', 'credit_quantity')
    op.drop_column('stock_movements', 'debit_quantity')
    op.drop_column('stock_movements', 'movement_number')