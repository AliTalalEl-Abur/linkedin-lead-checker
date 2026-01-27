"""Add subscription fields to User model

Revision ID: 002_add_subscription_fields
Revises: 001 (or previous migration)
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002_add_subscription_fields'
down_revision = None  # Update this if you have previous migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add subscription tracking fields to users table"""
    
    # Add subscription_status column
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('subscription_status', sa.String(length=50), nullable=True)
        )
        
        # Add monthly usage tracking columns
        batch_op.add_column(
            sa.Column('monthly_analyses_count', sa.Integer(), nullable=False, server_default='0')
        )
        batch_op.add_column(
            sa.Column('monthly_analyses_reset_at', sa.DateTime(timezone=True), nullable=True)
        )
        
        # Add indexes for better query performance
        batch_op.create_index('ix_users_stripe_customer_id', ['stripe_customer_id'], unique=False)
        batch_op.create_index('ix_users_stripe_subscription_id', ['stripe_subscription_id'], unique=False)


def downgrade() -> None:
    """Remove subscription tracking fields from users table"""
    
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Drop indexes
        batch_op.drop_index('ix_users_stripe_subscription_id')
        batch_op.drop_index('ix_users_stripe_customer_id')
        
        # Drop columns
        batch_op.drop_column('monthly_analyses_reset_at')
        batch_op.drop_column('monthly_analyses_count')
        batch_op.drop_column('subscription_status')
