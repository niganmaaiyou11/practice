from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Date, DateTime, Index, Text, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True, default=1)
    source: Mapped[str | None] = mapped_column(String(20), nullable=True, default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_date_provider", "date", "provider"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    rank_overall: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_gpqa: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_mmlu: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_mmlu_pro: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_math: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_humaneval: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_swebench: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_coding_arena: Mapped[float | None] = mapped_column(Float, nullable=True)
    # llm-stats.com v1.0 6-axis scores (0-1, group-level means)
    score_reasoning: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_coding: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_knowledge: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_tool_use: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_long_context: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_vision: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Category ranking scores fetched from /stats/v1/rankings (llm-stats.com)
    category_math_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    category_writing_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Scoring methodology version
    methodology_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tokens_per_second: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_input: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_output: Mapped[float | None] = mapped_column(Float, nullable=True)
    context_window: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    knowledge_cutoff: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modalities: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    # Modality discriminator + modality-generic metrics
    category: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    arena_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    output_resolution: Mapped[str | None] = mapped_column(String(30), nullable=True)
    latency: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        Index("idx_lb_provider_score", "provider", "overall_score"),
        Index("idx_lb_category_score", "category", "overall_score"),
    )


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(20), nullable=False)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    imap_server: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imap_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imap_password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    monitored_providers: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_email_account_user", "user_id"),
    )


class SyncedEmail(Base):
    __tablename__ = "synced_emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_accounts.id"), nullable=False, index=True)
    message_id: Mapped[str] = mapped_column(String(500), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    email_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parsed_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_usage_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("token_usage.id"), nullable=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("email_account_id", "message_id", name="uq_email_msg"),
        Index("idx_synced_email_date", "email_date"),
    )


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_accounts.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    emails_fetched: Mapped[int] = mapped_column(Integer, default=0)
    emails_parsed: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
