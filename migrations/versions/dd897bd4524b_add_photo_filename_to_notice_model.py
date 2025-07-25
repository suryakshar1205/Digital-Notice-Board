"""Add photo_filename to Notice model

Revision ID: dd897bd4524b
Revises: dc58652eb49f
Create Date: 2025-04-30 17:03:44.049342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd897bd4524b'
down_revision = 'dc58652eb49f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_filename', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notice', schema=None) as batch_op:
        batch_op.drop_column('photo_filename')

    # ### end Alembic commands ###
