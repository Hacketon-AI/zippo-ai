"""drop unused tables and columns

Revision ID: 7b3f9d21ac54
Revises: 0e2e7f152c29
Create Date: 2026-07-16 00:00:00.000000+00:00

Removes dead schema surface:
- conversation_sessions / chat_messages: never read or written by the app.
- ai_cache.source_refs / confidence_score: always NULL, no reader.
- feedback_corrections.priority: written as a constant, never read.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b3f9d21ac54'
down_revision: Union[str, None] = '0e2e7f152c29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_chat_messages_session_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_table('conversation_sessions')
    op.drop_column('ai_cache', 'source_refs')
    op.drop_column('ai_cache', 'confidence_score')
    op.drop_column('feedback_corrections', 'priority')


def downgrade() -> None:
    op.add_column(
        'feedback_corrections',
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column('ai_cache', sa.Column('confidence_score', sa.Float(), nullable=True))
    op.add_column('ai_cache', sa.Column('source_refs', sa.JSON(), nullable=True))
    op.create_table(
        'conversation_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)
