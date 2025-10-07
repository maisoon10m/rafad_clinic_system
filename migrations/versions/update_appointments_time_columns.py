"""
Migration script to update appointments table schema
Rename start_time to appointment_time and drop end_time column
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = 'update_appointments_time_columns'
down_revision = None  # Set to your last migration, or None for initial migration
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('appointments') as batch_op:
        # Rename start_time to appointment_time
        batch_op.alter_column('start_time', new_column_name='appointment_time', 
                             existing_type=sa.Time())
        
        # Drop end_time column - this is not used in the model
        batch_op.drop_column('end_time')

def downgrade():
    with op.batch_alter_table('appointments') as batch_op:
        # Add end_time column back
        batch_op.add_column(sa.Column('end_time', sa.Time(), nullable=True))
        
        # Rename appointment_time back to start_time
        batch_op.alter_column('appointment_time', new_column_name='start_time', 
                             existing_type=sa.Time())