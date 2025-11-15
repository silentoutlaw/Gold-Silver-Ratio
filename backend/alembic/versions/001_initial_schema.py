"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2025-11-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types using DO blocks to check if they exist
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'assettype') THEN
                CREATE TYPE assettype AS ENUM ('metal', 'fx', 'rate', 'index', 'macro', 'commodity', 'equity', 'etf');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'regimetype') THEN
                CREATE TYPE regimetype AS ENUM ('risk_off_deflation', 'risk_on_reflation', 'tightening_strong_usd', 'easing_weak_usd', 'crisis', 'normal', 'custom');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alerttype') THEN
                CREATE TYPE alerttype AS ENUM ('ratio_band', 'macro_event', 'composite_signal', 'threshold');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'alertstatus') THEN
                CREATE TYPE alertstatus AS ENUM ('active', 'triggered', 'dismissed', 'expired');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'prompttype') THEN
                CREATE TYPE prompttype AS ENUM ('system', 'user', 'tool_template');
            END IF;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'messagerole') THEN
                CREATE TYPE messagerole AS ENUM ('system', 'user', 'assistant', 'tool');
            END IF;
        END $$;
    """)

    # Define enum types for use in table definitions
    asset_type_enum = postgresql.ENUM(
        'metal', 'fx', 'rate', 'index', 'macro', 'commodity', 'equity', 'etf',
        name='assettype', create_type=False
    )
    regime_type_enum = postgresql.ENUM(
        'risk_off_deflation', 'risk_on_reflation', 'tightening_strong_usd',
        'easing_weak_usd', 'crisis', 'normal', 'custom',
        name='regimetype', create_type=False
    )
    alert_type_enum = postgresql.ENUM(
        'ratio_band', 'macro_event', 'composite_signal', 'threshold',
        name='alerttype', create_type=False
    )
    alert_status_enum = postgresql.ENUM(
        'active', 'triggered', 'dismissed', 'expired',
        name='alertstatus', create_type=False
    )
    prompt_type_enum = postgresql.ENUM(
        'system', 'user', 'tool_template',
        name='prompttype', create_type=False
    )
    message_role_enum = postgresql.ENUM(
        'system', 'user', 'assistant', 'tool',
        name='messagerole', create_type=False
    )

    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', asset_type_enum, nullable=False),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)
    op.create_index(op.f('ix_assets_symbol'), 'assets', ['symbol'], unique=True)
    op.create_index(op.f('ix_assets_type'), 'assets', ['type'], unique=False)

    # Create prices table
    op.create_table(
        'prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('open', sa.Float(), nullable=True),
        sa.Column('high', sa.Float(), nullable=True),
        sa.Column('low', sa.Float(), nullable=True),
        sa.Column('close', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prices_id'), 'prices', ['id'], unique=False)
    op.create_index(op.f('ix_prices_asset_id'), 'prices', ['asset_id'], unique=False)
    op.create_index(op.f('ix_prices_timestamp'), 'prices', ['timestamp'], unique=False)
    op.create_index('ix_prices_asset_timestamp', 'prices', ['asset_id', 'timestamp'], unique=False)

    # Create macro_series table
    op.create_table(
        'macro_series',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_macro_series_id'), 'macro_series', ['id'], unique=False)
    op.create_index(op.f('ix_macro_series_code'), 'macro_series', ['code'], unique=True)

    # Create macro_values table
    op.create_table(
        'macro_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('macro_series_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('revision', sa.Integer(), nullable=True),
        sa.Column('release_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['macro_series_id'], ['macro_series.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_macro_values_id'), 'macro_values', ['id'], unique=False)
    op.create_index(op.f('ix_macro_values_macro_series_id'), 'macro_values', ['macro_series_id'], unique=False)
    op.create_index(op.f('ix_macro_values_date'), 'macro_values', ['date'], unique=False)
    op.create_index('ix_macro_values_series_date', 'macro_values', ['macro_series_id', 'date'], unique=False)

    # Create derived_metrics table
    op.create_table(
        'derived_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('computation_method', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_derived_metrics_id'), 'derived_metrics', ['id'], unique=False)
    op.create_index(op.f('ix_derived_metrics_name'), 'derived_metrics', ['name'], unique=True)

    # Create metric_values table
    op.create_table(
        'metric_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('computation_notes', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['metric_id'], ['derived_metrics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metric_values_id'), 'metric_values', ['id'], unique=False)
    op.create_index(op.f('ix_metric_values_metric_id'), 'metric_values', ['metric_id'], unique=False)
    op.create_index(op.f('ix_metric_values_timestamp'), 'metric_values', ['timestamp'], unique=False)
    op.create_index('ix_metric_values_metric_timestamp', 'metric_values', ['metric_id', 'timestamp'], unique=False)

    # Create regimes table
    op.create_table(
        'regimes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=False),
        sa.Column('regime_type', regime_type_enum, nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('methodology_version', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regimes_id'), 'regimes', ['id'], unique=False)
    op.create_index(op.f('ix_regimes_regime_type'), 'regimes', ['regime_type'], unique=False)
    op.create_index(op.f('ix_regimes_start_date'), 'regimes', ['start_date'], unique=False)
    op.create_index(op.f('ix_regimes_end_date'), 'regimes', ['end_date'], unique=False)

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('type', alert_type_enum, nullable=False),
        sa.Column('status', alert_status_enum, nullable=False),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('ix_alerts_user_id'), 'alerts', ['user_id'], unique=False)
    op.create_index(op.f('ix_alerts_type'), 'alerts', ['type'], unique=False)
    op.create_index(op.f('ix_alerts_status'), 'alerts', ['status'], unique=False)
    op.create_index(op.f('ix_alerts_created_at'), 'alerts', ['created_at'], unique=False)
    op.create_index(op.f('ix_alerts_triggered_at'), 'alerts', ['triggered_at'], unique=False)

    # Create prompts table
    op.create_table(
        'prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', prompt_type_enum, nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prompts_id'), 'prompts', ['id'], unique=False)
    op.create_index(op.f('ix_prompts_name'), 'prompts', ['name'], unique=False)
    op.create_index(op.f('ix_prompts_type'), 'prompts', ['type'], unique=False)
    op.create_index(op.f('ix_prompts_is_active'), 'prompts', ['is_active'], unique=False)
    op.create_index('ix_prompts_name_version', 'prompts', ['name', 'version'], unique=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('context_type', sa.String(length=50), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'], unique=False)
    op.create_index(op.f('ix_conversations_context_type'), 'conversations', ['context_type'], unique=False)
    op.create_index(op.f('ix_conversations_created_at'), 'conversations', ['created_at'], unique=False)

    # Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_id'), 'conversation_messages', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_conversation_id'), 'conversation_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_role'), 'conversation_messages', ['role'], unique=False)
    op.create_index(op.f('ix_conversation_messages_created_at'), 'conversation_messages', ['created_at'], unique=False)
    op.create_index('ix_conversation_messages_conv_created', 'conversation_messages', ['conversation_id', 'created_at'], unique=False)

    # Enable TimescaleDB extension if available (requires superuser)
    # This will be run manually or via a separate migration
    # op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    # Convert prices and metric_values to hypertables (requires TimescaleDB)
    # These will be executed manually after TimescaleDB is installed
    # op.execute("SELECT create_hypertable('prices', 'timestamp', if_not_exists => TRUE);")
    # op.execute("SELECT create_hypertable('metric_values', 'timestamp', if_not_exists => TRUE);")


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('prompts')
    op.drop_table('alerts')
    op.drop_table('regimes')
    op.drop_table('metric_values')
    op.drop_table('derived_metrics')
    op.drop_table('macro_values')
    op.drop_table('macro_series')
    op.drop_table('prices')
    op.drop_table('assets')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS messagerole')
    op.execute('DROP TYPE IF EXISTS prompttype')
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS alerttype')
    op.execute('DROP TYPE IF EXISTS regimetype')
    op.execute('DROP TYPE IF EXISTS assettype')
