"""Create topic, content, and metric tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-12
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("external_id", sa.String(500), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("trend_score", sa.Float()),
        sa.Column("topic_score", sa.Float()),
        sa.Column("status", sa.String(32), server_default="collected", nullable=False),
        sa.Column("metadata_json", sa.Text()),
        sa.CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 10)", name="ck_topics_trend_score"),
        sa.CheckConstraint("topic_score IS NULL OR (topic_score >= 0 AND topic_score <= 10)", name="ck_topics_topic_score"),
        sa.UniqueConstraint("source", "external_id", name="uq_topics_source_external_id"),
    )
    op.create_index("ix_topics_title", "topics", ["title"])
    op.create_table(
        "content_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), server_default="", nullable=False),
        sa.Column("prompt_version", sa.String(100)),
        sa.Column("model_version", sa.String(100)),
        sa.Column("ai_generated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("ai_label_status", sa.String(32), server_default="not_applicable", nullable=False),
        sa.Column("fact_check_status", sa.String(32), server_default="unchecked", nullable=False),
        sa.Column("approval_status", sa.String(32), server_default="pending", nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("publish_status", sa.String(32), server_default="draft", nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("platform_content_id", sa.String(255)),
        sa.CheckConstraint("approval_status IN ('pending', 'approved', 'rejected')", name="ck_content_approval_status"),
        sa.CheckConstraint("publish_status IN ('draft', 'ready', 'published', 'failed')", name="ck_content_publish_status"),
    )
    op.create_index("ix_content_items_topic_id", "content_items", ["topic_id"])
    op.create_table(
        "content_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content_item_id", sa.Integer(), sa.ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("window", sa.String(32), nullable=False),
        sa.Column("views", sa.Integer()),
        sa.Column("likes", sa.Integer()),
        sa.Column("comments", sa.Integer()),
        sa.Column("shares", sa.Integer()),
        sa.Column("followers_gained", sa.Integer()),
        sa.Column("conversions", sa.Integer()),
        sa.Column("cost_amount", sa.Float()),
        sa.Column("cost_currency", sa.String(3)),
        sa.UniqueConstraint("content_item_id", "captured_at", name="uq_metrics_content_capture"),
    )
    op.create_index("ix_content_metrics_content_item_id", "content_metrics", ["content_item_id"])


def downgrade() -> None:
    op.drop_index("ix_content_metrics_content_item_id", table_name="content_metrics")
    op.drop_table("content_metrics")
    op.drop_index("ix_content_items_topic_id", table_name="content_items")
    op.drop_table("content_items")
    op.drop_index("ix_topics_title", table_name="topics")
    op.drop_table("topics")
