"""add_advanced_maintenance_planning_tables

Revision ID: a7486a6e8cfb
Revises: 6bc3647d3d08
Create Date: 2025-10-01 21:01:54.519179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7486a6e8cfb'
down_revision: Union[str, Sequence[str], None] = '6bc3647d3d08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create advanced_maintenance_plans table
    op.create_table('advanced_maintenance_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rrule', sa.Text(), nullable=False),
        sa.Column('gate_filter', sa.JSON(), nullable=True),
        sa.Column('task_template', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('updated_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_advanced_maintenance_plans_id', 'id'),
        sa.Index('ix_advanced_maintenance_plans_org_id', 'org_id')
    )
    
    # Create advanced_scheduled_jobs table
    op.create_table('advanced_scheduled_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('advanced_maintenance_plans.id'), nullable=False),
        sa.Column('gate_id', sa.Integer(), sa.ForeignKey('gates.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='scheduled'),
        sa.Column('priority', sa.String(10), nullable=False, default='medium'),
        sa.Column('assigned_to_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('required_tools', sa.JSON(), nullable=True),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('completion_notes', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_advanced_scheduled_jobs_id', 'id'),
        sa.Index('ix_advanced_scheduled_jobs_org_id', 'org_id'),
        sa.Index('ix_advanced_scheduled_jobs_scheduled_date', 'scheduled_date'),
        sa.Index('ix_advanced_scheduled_jobs_due_date', 'due_date'),
        sa.Index('ix_advanced_scheduled_jobs_status', 'status')
    )
    
    # Create advanced_maintenance_calendars table
    op.create_table('advanced_maintenance_calendars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('color', sa.String(7), nullable=True, default='#007acc'),
        sa.Column('filter_config', sa.JSON(), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False, default='UTC'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_advanced_maintenance_calendars_id', 'id')
    )
    
    # Create advanced_maintenance_notifications table
    op.create_table('advanced_maintenance_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), sa.ForeignKey('advanced_scheduled_jobs.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notification_type', sa.String(20), nullable=False),
        sa.Column('delivery_method', sa.String(10), nullable=False),
        sa.Column('delivery_address', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_advanced_maintenance_notifications_id', 'id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('advanced_maintenance_notifications')
    op.drop_table('advanced_maintenance_calendars') 
    op.drop_table('advanced_scheduled_jobs')
    op.drop_table('advanced_maintenance_plans')
