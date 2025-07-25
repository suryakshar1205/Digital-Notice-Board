"""Add sections column to timetable table

Revision ID: dc58652eb49f
Revises: 
Create Date: 2025-04-21 13:09:43.689215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc58652eb49f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('timetable', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sections', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('timetable', schema=None) as batch_op:
        batch_op.drop_column('sections')

    # ### end Alembic commands ###
