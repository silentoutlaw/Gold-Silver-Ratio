"""
SQLAlchemy database models for GSR Analytics.
Defines all tables and relationships as per the Plan specification.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AssetType(str, enum.Enum):
    """Asset type enumeration."""

    METAL = "metal"
    FX = "fx"
    RATE = "rate"
    INDEX = "index"
    MACRO = "macro"
    COMMODITY = "commodity"
    EQUITY = "equity"
    ETF = "etf"


class Asset(Base):
    """Assets table: metals, FX, rates, indices, commodities, etc."""

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(AssetType), nullable=False, index=True)
    source = Column(String(100))  # Data source identifier
    extra_data = Column(JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    prices = relationship("Price", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Asset(symbol={self.symbol}, name={self.name}, type={self.type})>"


class Price(Base):
    """Time-series price data for all assets."""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Float)  # Nullable for some assets
    source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    asset = relationship("Asset", back_populates="prices")

    # Indexes
    __table_args__ = (Index("ix_prices_asset_timestamp", "asset_id", "timestamp"),)

    def __repr__(self) -> str:
        return f"<Price(asset_id={self.asset_id}, timestamp={self.timestamp}, close={self.close})>"


class MacroSeries(Base):
    """Macro economic series definitions (e.g., CPI, unemployment rate)."""

    __tablename__ = "macro_series"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    frequency = Column(String(20))  # daily, weekly, monthly, quarterly, annual
    source = Column(String(100))  # FRED, BLS, etc.
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    values = relationship("MacroValue", back_populates="series", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<MacroSeries(code={self.code}, name={self.name})>"


class MacroValue(Base):
    """Time-series values for macro economic series."""

    __tablename__ = "macro_values"

    id = Column(Integer, primary_key=True, index=True)
    macro_series_id = Column(Integer, ForeignKey("macro_series.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    revision = Column(Integer, default=0)  # For tracking data revisions
    release_time = Column(DateTime(timezone=True))  # When data was officially released
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    series = relationship("MacroSeries", back_populates="values")

    # Indexes
    __table_args__ = (Index("ix_macro_values_series_date", "macro_series_id", "date"),)

    def __repr__(self) -> str:
        return f"<MacroValue(series_id={self.macro_series_id}, date={self.date}, value={self.value})>"


class DerivedMetric(Base):
    """Derived metrics definitions (GSR, correlations, z-scores, etc.)."""

    __tablename__ = "derived_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    computation_method = Column(Text)  # Description of how it's computed
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    values = relationship("MetricValue", back_populates="metric", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DerivedMetric(name={self.name})>"


class MetricValue(Base):
    """Time-series values for derived metrics."""

    __tablename__ = "metric_values"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("derived_metrics.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    value = Column(Float, nullable=False)
    computation_notes = Column(Text)
    extra_data = Column(JSON)  # Store additional computed values
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    metric = relationship("DerivedMetric", back_populates="values")

    # Indexes
    __table_args__ = (Index("ix_metric_values_metric_timestamp", "metric_id", "timestamp"),)

    def __repr__(self) -> str:
        return f"<MetricValue(metric_id={self.metric_id}, timestamp={self.timestamp}, value={self.value})>"


class RegimeType(str, enum.Enum):
    """Macro regime type enumeration."""

    RISK_OFF_DEFLATION = "risk_off_deflation"
    RISK_ON_REFLATION = "risk_on_reflation"
    TIGHTENING_STRONG_USD = "tightening_strong_usd"
    EASING_WEAK_USD = "easing_weak_usd"
    CRISIS = "crisis"
    NORMAL = "normal"
    CUSTOM = "custom"


class Regime(Base):
    """Macro regime classifications."""

    __tablename__ = "regimes"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), nullable=False)
    regime_type = Column(SQLEnum(RegimeType), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), index=True)
    methodology_version = Column(String(50))
    notes = Column(Text)
    extra_data = Column(JSON)  # Store regime characteristics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Regime(label={self.label}, type={self.regime_type}, start={self.start_date})>"


class AlertType(str, enum.Enum):
    """Alert type enumeration."""

    RATIO_BAND = "ratio_band"
    MACRO_EVENT = "macro_event"
    COMPOSITE_SIGNAL = "composite_signal"
    THRESHOLD = "threshold"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration."""

    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class Alert(Base):
    """User-configured alerts."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Optional user association
    type = Column(SQLEnum(AlertType), nullable=False, index=True)
    status = Column(SQLEnum(AlertStatus), nullable=False, default=AlertStatus.ACTIVE, index=True)
    payload = Column(JSON, nullable=False)  # Alert configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    triggered_at = Column(DateTime(timezone=True), index=True)
    dismissed_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Alert(type={self.type}, status={self.status}, created={self.created_at})>"


class PromptType(str, enum.Enum):
    """Prompt type enumeration."""

    SYSTEM = "system"
    USER = "user"
    TOOL_TEMPLATE = "tool_template"


class Prompt(Base):
    """AI prompt templates storage."""

    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(SQLEnum(PromptType), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    body = Column(Text, nullable=False)
    extra_data = Column(JSON)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Unique constraint on name + version
    __table_args__ = (Index("ix_prompts_name_version", "name", "version", unique=True),)

    def __repr__(self) -> str:
        return f"<Prompt(name={self.name}, type={self.type}, version={self.version})>"


class Conversation(Base):
    """AI conversation sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    context_type = Column(String(50), index=True)  # strategy, dashboard, experiment, etc.
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    messages = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, type={self.context_type}, created={self.created_at})>"


class MessageRole(str, enum.Enum):
    """Message role enumeration."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ConversationMessage(Base):
    """Individual messages in AI conversations."""

    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer, ForeignKey("conversations.id"), nullable=False, index=True
    )
    role = Column(SQLEnum(MessageRole), nullable=False, index=True)
    content = Column(Text, nullable=False)
    model_name = Column(String(100))
    provider = Column(String(50))  # openai, anthropic, google
    tokens_used = Column(Integer)
    extra_data = Column(JSON)  # Tool calls, function results, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index("ix_conversation_messages_conv_created", "conversation_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage(conv_id={self.conversation_id}, role={self.role}, provider={self.provider})>"
