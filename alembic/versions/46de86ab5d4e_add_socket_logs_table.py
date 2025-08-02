"""add_socket_logs_table

Revision ID: 46de86ab5d4e
Revises: 56f60bc1e29c
Create Date: 2025-08-02 18:46:51.023144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46de86ab5d4e'
down_revision: Union[str, None] = '56f60bc1e29c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### manually added socket_logs table ###
    op.create_table('socket_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('socket_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('user_role', sa.String(), nullable=True),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('request_data', sa.JSON(), nullable=True),
        sa.Column('response_data', sa.JSON(), nullable=True),
        sa.Column('patient_latitude', sa.String(), nullable=True),
        sa.Column('patient_longitude', sa.String(), nullable=True),
        sa.Column('hospital_id', sa.Integer(), nullable=True),
        sa.Column('hospital_name', sa.String(), nullable=True),
        sa.Column('distance_km', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_duration', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_socket_logs_event_type'), 'socket_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_socket_logs_hospital_id'), 'socket_logs', ['hospital_id'], unique=False)
    op.create_index(op.f('ix_socket_logs_id'), 'socket_logs', ['id'], unique=False)
    op.create_index(op.f('ix_socket_logs_socket_id'), 'socket_logs', ['socket_id'], unique=False)
    op.create_index(op.f('ix_socket_logs_user_id'), 'socket_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_socket_logs_user_role'), 'socket_logs', ['user_role'], unique=False)
    op.create_index(op.f('ix_socket_logs_created_at'), 'socket_logs', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### manually added socket_logs table removal ###
    op.drop_index(op.f('ix_socket_logs_created_at'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_user_role'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_user_id'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_socket_id'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_id'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_hospital_id'), table_name='socket_logs')
    op.drop_index(op.f('ix_socket_logs_event_type'), table_name='socket_logs')
    op.drop_table('socket_logs')
    # ### end Alembic commands ###
