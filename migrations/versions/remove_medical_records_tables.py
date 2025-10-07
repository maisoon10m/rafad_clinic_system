"""
Migration to drop medical records tables that are no longer needed
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_medical_records_tables'
down_revision = 'add_last_login_column'
branch_labels = None
depends_on = None


def upgrade():
    """Drop medical records related tables"""
    # Drop tables in the correct order (to avoid foreign key constraints)
    op.drop_table('test_results')
    op.drop_table('treatments')
    op.drop_table('prescriptions')
    op.drop_table('diagnoses')
    op.drop_table('medical_records')


def downgrade():
    """
    This downgrade is intentionally left empty as we don't want to restore
    the medical records tables if someone downgrades.
    """
    pass