"""empty message

Revision ID: 3c85c65c9b1f
Revises: ee2268062b9f
Create Date: 2023-03-26 18:50:14.541419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c85c65c9b1f'
down_revision = 'ee2268062b9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_time', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
        batch_op.add_column(sa.Column('updated_time', sa.DateTime(), nullable=False, server_default=sa.text('now()')))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('updated_time')
        batch_op.drop_column('created_time')

    # ### end Alembic commands ###