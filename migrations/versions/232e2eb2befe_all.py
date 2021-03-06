"""all

Revision ID: 232e2eb2befe
Revises: 
Create Date: 2020-12-09 20:41:54.431157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '232e2eb2befe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('listing_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_first_name'), 'user', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_last_name'), 'user', ['last_name'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('listing',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('listing_date', sa.Date(), nullable=True),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=40), nullable=True),
    sa.Column('address_1', sa.String(length=50), nullable=True),
    sa.Column('address_2', sa.String(length=50), nullable=True),
    sa.Column('post_code', sa.String(length=10), nullable=True),
    sa.Column('outgoing', sa.Boolean(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['source_id'], ['listing_source.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_collate='utf8_general_ci',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_listing_listing_date'), 'listing', ['listing_date'], unique=False)
    op.create_index(op.f('ix_listing_user_id'), 'listing', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_listing_user_id'), table_name='listing')
    op.drop_index(op.f('ix_listing_listing_date'), table_name='listing')
    op.drop_table('listing')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_last_name'), table_name='user')
    op.drop_index(op.f('ix_user_first_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('listing_source')
    # ### end Alembic commands ###
