"""empty message

Revision ID: b37e2e366de7
Revises: 
Create Date: 2019-05-28 09:25:57.945264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b37e2e366de7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('kgs_username', sa.String(length=64), nullable=True),
    sa.Column('ayd_member', sa.Boolean(), nullable=True),
    sa.Column('eyd_member', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_ayd_member'), 'users', ['ayd_member'], unique=False)
    op.create_index(op.f('ix_users_eyd_member'), 'users', ['eyd_member'], unique=False)
    op.create_index(op.f('ix_users_kgs_username'), 'users', ['kgs_username'], unique=True)
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tournament', sa.String(length=128), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('round', sa.Integer(), nullable=True),
    sa.Column('black', sa.String(length=64), nullable=True),
    sa.Column('white', sa.String(length=64), nullable=True),
    sa.Column('b_win', sa.Boolean(), nullable=True),
    sa.Column('w_win', sa.Boolean(), nullable=True),
    sa.Column('ayd_game', sa.Boolean(), nullable=True),
    sa.Column('eyd_game', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['black'], ['users.kgs_username'], ),
    sa.ForeignKeyConstraint(['white'], ['users.kgs_username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_games_ayd_game'), 'games', ['ayd_game'], unique=False)
    op.create_index(op.f('ix_games_date'), 'games', ['date'], unique=False)
    op.create_index(op.f('ix_games_eyd_game'), 'games', ['eyd_game'], unique=False)
    op.create_index(op.f('ix_games_round'), 'games', ['round'], unique=False)
    op.create_index(op.f('ix_games_tournament'), 'games', ['tournament'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_games_tournament'), table_name='games')
    op.drop_index(op.f('ix_games_round'), table_name='games')
    op.drop_index(op.f('ix_games_eyd_game'), table_name='games')
    op.drop_index(op.f('ix_games_date'), table_name='games')
    op.drop_index(op.f('ix_games_ayd_game'), table_name='games')
    op.drop_table('games')
    op.drop_index(op.f('ix_users_kgs_username'), table_name='users')
    op.drop_index(op.f('ix_users_eyd_member'), table_name='users')
    op.drop_index(op.f('ix_users_ayd_member'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
