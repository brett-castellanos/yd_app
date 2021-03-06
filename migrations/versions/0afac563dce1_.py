"""empty message

Revision ID: 0afac563dce1
Revises: b37e2e366de7
Create Date: 2019-05-28 10:15:47.454433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0afac563dce1'
down_revision = 'b37e2e366de7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kgs_games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('white', sa.String(length=64), nullable=True),
    sa.Column('black', sa.String(length=64), nullable=True),
    sa.Column('setup', sa.String(length=64), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('w_win', sa.Boolean(), nullable=True),
    sa.Column('b_win', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kgs_games_date'), 'kgs_games', ['date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_kgs_games_date'), table_name='kgs_games')
    op.drop_table('kgs_games')
    # ### end Alembic commands ###
