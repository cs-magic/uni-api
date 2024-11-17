"""Initial migration

Revision ID: dd55b5b54531
Revises: e257c6a7b6c8
Create Date: 2024-11-14 08:04:04.311046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd55b5b54531'
down_revision: Union[str, None] = 'e257c6a7b6c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('stripe_payment_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_id'), ['id'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('email', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('hashed_password', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('full_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('disabled', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('oauth_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('credits', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_phone'), ['phone'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_phone'))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('credits')
        batch_op.drop_column('oauth_id')
        batch_op.drop_column('oauth_provider')
        batch_op.drop_column('disabled')
        batch_op.drop_column('full_name')
        batch_op.drop_column('hashed_password')
        batch_op.drop_column('phone')
        batch_op.drop_column('email')
        batch_op.drop_column('username')

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_id'))

    op.drop_table('transactions')
    # ### end Alembic commands ###