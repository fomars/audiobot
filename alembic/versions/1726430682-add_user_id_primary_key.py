"""

Revision ID: 7a5026ea0560
Revises: 05543f5dc7aa
Create Date: 2024-09-15 22:04:42.604507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a5026ea0560'
down_revision = '05543f5dc7aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False))
    op.execute('CREATE SEQUENCE users_id_seq')
    op.execute('ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval(\'users_id_seq\')')

    op.execute("ALTER TABLE users DROP CONSTRAINT users_pkey")
    op.alter_column('users', 'tg_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.create_index(op.f('ix_users_tg_id'), 'users', ['tg_id'], unique=True)
    op.execute('ALTER TABLE users ADD PRIMARY KEY (id)')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_tg_id'), table_name='users')

    op.execute('ALTER TABLE users DROP CONSTRAINT users_pkey')

    op.alter_column('users', 'tg_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.execute('ALTER TABLE users ADD PRIMARY KEY (tg_id)')

    op.drop_column('users', 'id')
    op.execute('DROP SEQUENCE users_id_seq')
    # ### end Alembic commands ###
