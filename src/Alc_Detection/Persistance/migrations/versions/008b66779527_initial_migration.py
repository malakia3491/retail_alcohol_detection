"""Initial migration

Revision ID: 008b66779527
Revises: 2b9b91c22243
Create Date: 2025-05-08 08:21:08.711495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008b66779527'
down_revision: Union[str, None] = '2b9b91c22243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('person_incidents',
    sa.Column('person_id', sa.UUID(), nullable=True),
    sa.Column('incident_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_person_incidents_id'), 'person_incidents', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_person_incidents_id'), table_name='person_incidents')
    op.drop_table('person_incidents')
    # ### end Alembic commands ###
