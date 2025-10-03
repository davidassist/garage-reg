"""add_field_forms_state_machine_and_photos

Revision ID: cea61e0e08a6
Revises: 177019ee0ca0
Create Date: 2025-10-02 06:03:55.578340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cea61e0e08a6'
down_revision: Union[str, Sequence[str], None] = '177019ee0ca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Add state machine and field form fields to inspections table
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        # State machine
        batch_op.add_column(sa.Column('state', sa.String(20), nullable=False, default='draft'))
        
        # Field form specific fields  
        batch_op.add_column(sa.Column('mobile_device_id', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('offline_started_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('sync_status', sa.String(20), nullable=False, default='synced'))
        batch_op.add_column(sa.Column('last_sync_at', sa.DateTime(), nullable=True))
        
        # Conflict resolution
        batch_op.add_column(sa.Column('conflict_data', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('merge_strategy', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('conflict_resolved_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('conflict_resolved_by_id', sa.Integer(), nullable=True))
        
        # Photo documentation requirements
        batch_op.add_column(sa.Column('required_photos', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('uploaded_photos', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('photo_validation_status', sa.String(20), nullable=False, default='pending'))
        
        # Add foreign key for conflict resolver
        batch_op.create_foreign_key('fk_conflict_resolved_by', 'users', ['conflict_resolved_by_id'], ['id'])
        
        # Add indexes for field forms
        batch_op.create_index('ix_inspections_state', ['state'])
        batch_op.create_index('ix_inspections_sync_status', ['sync_status'])
        batch_op.create_index('ix_inspections_mobile_device', ['mobile_device_id'])
        batch_op.create_index('ix_inspections_photo_status', ['photo_validation_status'])
    
    # Create inspection_photos table
    op.create_table(
        'inspection_photos',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        
        # References
        sa.Column('inspection_id', sa.Integer(), sa.ForeignKey('inspections.id'), nullable=False, index=True),
        sa.Column('inspection_item_id', sa.Integer(), sa.ForeignKey('inspection_items.id'), nullable=True, index=True),
        
        # Photo metadata
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # S3 storage information
        sa.Column('s3_bucket', sa.String(100), nullable=False),
        sa.Column('s3_key', sa.String(500), nullable=False),
        sa.Column('s3_url', sa.String(1000), nullable=True),
        
        # File metadata
        sa.Column('original_filename', sa.String(255), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        
        # Image metadata
        sa.Column('width_pixels', sa.Integer(), nullable=True),
        sa.Column('height_pixels', sa.Integer(), nullable=True),
        
        # GPS and location data
        sa.Column('gps_latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('gps_longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('location_accuracy_meters', sa.Numeric(10, 2), nullable=True),
        
        # Capture context
        sa.Column('captured_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('captured_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('device_info', sa.JSON(), nullable=True),
        
        # Upload tracking
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('upload_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('upload_attempts', sa.Integer(), default=0, nullable=False),
        sa.Column('upload_error', sa.Text(), nullable=True),
        
        # Validation and requirements
        sa.Column('is_required', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_validated', sa.Boolean(), default=False, nullable=False),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(), default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True)
    )
    
    # Add indexes for inspection_photos
    op.create_index('ix_inspection_photos_inspection', 'inspection_photos', ['inspection_id'])
    op.create_index('ix_inspection_photos_item', 'inspection_photos', ['inspection_item_id'])
    op.create_index('ix_inspection_photos_category', 'inspection_photos', ['category'])
    op.create_index('ix_inspection_photos_captured', 'inspection_photos', ['captured_at'])
    op.create_index('ix_inspection_photos_upload_status', 'inspection_photos', ['upload_status'])


def downgrade() -> None:
    """Downgrade schema."""
    
    # Drop inspection_photos table
    op.drop_index('ix_inspection_photos_upload_status', 'inspection_photos')
    op.drop_index('ix_inspection_photos_captured', 'inspection_photos')
    op.drop_index('ix_inspection_photos_category', 'inspection_photos')
    op.drop_index('ix_inspection_photos_item', 'inspection_photos')
    op.drop_index('ix_inspection_photos_inspection', 'inspection_photos')
    op.drop_table('inspection_photos')
    
    # Remove field form fields from inspections table
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        # Remove indexes
        batch_op.drop_index('ix_inspections_photo_status')
        batch_op.drop_index('ix_inspections_mobile_device')
        batch_op.drop_index('ix_inspections_sync_status')
        batch_op.drop_index('ix_inspections_state')
        
        # Remove foreign key
        batch_op.drop_constraint('fk_conflict_resolved_by', type_='foreignkey')
        
        # Remove columns
        batch_op.drop_column('photo_validation_status')
        batch_op.drop_column('uploaded_photos')
        batch_op.drop_column('required_photos')
        batch_op.drop_column('conflict_resolved_by_id')
        batch_op.drop_column('conflict_resolved_at')
        batch_op.drop_column('merge_strategy')
        batch_op.drop_column('conflict_data')
        batch_op.drop_column('last_sync_at')
        batch_op.drop_column('sync_status')
        batch_op.drop_column('offline_started_at')
        batch_op.drop_column('mobile_device_id')
        batch_op.drop_column('state')
