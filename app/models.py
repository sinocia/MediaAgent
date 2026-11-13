"""Relational models for topics, generated content, and metric snapshots."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_topics_source_external_id"),
        CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 10)", name="ck_topics_trend_score"),
        CheckConstraint("topic_score IS NULL OR (topic_score >= 0 AND topic_score <= 10)", name="ck_topics_topic_score"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[str] = mapped_column(String(500), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    trend_score: Mapped[float | None] = mapped_column(Float)
    topic_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="collected", nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)

    content_items: Mapped[list["ContentItem"]] = relationship(back_populates="topic")


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (
        CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name="ck_content_approval_status"),
        CheckConstraint("publish_status IN ('draft', 'ready', 'published', 'failed')", name="ck_content_publish_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(100))
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_label_status: Mapped[str] = mapped_column(String(32), default="not_applicable", nullable=False)
    fact_check_status: Mapped[str] = mapped_column(String(32), default="unchecked", nullable=False)
    approval_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    publish_status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform_content_id: Mapped[str | None] = mapped_column(String(255))

    topic: Mapped[Topic | None] = relationship(back_populates="content_items")
    metrics: Mapped[list["ContentMetric"]] = relationship(back_populates="content_item", cascade="all, delete-orphan")


class ContentMetric(Base):
    __tablename__ = "content_metrics"
    __table_args__ = (UniqueConstraint("content_item_id", "captured_at", name="uq_metrics_content_capture"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_item_id: Mapped[int] = mapped_column(ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    window: Mapped[str] = mapped_column(String(32), nullable=False)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    followers_gained: Mapped[int | None] = mapped_column(Integer)
    conversions: Mapped[int | None] = mapped_column(Integer)
    cost_amount: Mapped[float | None] = mapped_column(Float)
    cost_currency: Mapped[str | None] = mapped_column(String(3))
    content_item: Mapped[ContentItem] = relationship(back_populates="metrics")
