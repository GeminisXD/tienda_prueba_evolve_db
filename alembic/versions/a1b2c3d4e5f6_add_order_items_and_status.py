"""add order items, order status and stripe session

Revision ID: a1b2c3d4e5f6
Revises: 076f7565b5b3
Create Date: 2026-11-15 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '076f7565b5b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE products SET stock = 0 WHERE stock IS NULL")
    op.alter_column('products', 'stock', existing_type=sa.Integer(), nullable=False, server_default='0')
    op.add_column('orders', sa.Column('status', sa.String(), nullable=False, server_default='pending'))
    op.add_column('orders', sa.Column('stripe_session_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_orders_stripe_session_id'), 'orders', ['stripe_session_id'])
    op.alter_column('orders', 'created_at', existing_type=sa.DateTime(), type_=sa.DateTime(timezone=True))
    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')
    op.alter_column('orders', 'created_at', existing_type=sa.DateTime(timezone=True), type_=sa.DateTime())
    op.drop_index(op.f('ix_orders_stripe_session_id'), table_name='orders')
    op.drop_column('orders', 'stripe_session_id')
    op.drop_column('orders', 'status')
    op.alter_column('products', 'stock', existing_type=sa.Integer(), nullable=True, server_default=None)
