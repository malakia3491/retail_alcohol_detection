"""Initial migration

Revision ID: 62622e6be023
Revises: 
Create Date: 2025-04-23 20:51:19.651051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62622e6be023'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('embedding_models', sa.Column('embedding_shape', sa.Integer(), nullable=True))
    op.add_column('embeddings', sa.Column('image_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'embeddings', 'product_images', ['image_id'], ['id'])
    op.alter_column('products', 'label',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True,
               existing_server_default=sa.text("nextval('products_label_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'label',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True,
               existing_server_default=sa.text("nextval('products_label_seq'::regclass)"))
    op.drop_constraint(None, 'embeddings', type_='foreignkey')
    op.drop_column('embeddings', 'image_id')
    op.drop_column('embedding_models', 'embedding_shape')
    # ### end Alembic commands ###
