"""empty message

Revision ID: b862e8b7fd7b
Revises: 1a59846f54c1
Create Date: 2019-05-27 21:47:58.784704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b862e8b7fd7b'
down_revision = '1a59846f54c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uniq_con_1', 'game', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uniq_con_1', 'game', ['tournament', 'date', 'round', 'black', 'white'])
    # ### end Alembic commands ###
