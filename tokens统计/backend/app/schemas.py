from __future__ import annotations
from datetime import date as date_type, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TokenUsageCreate(BaseModel):
    date: date_type
    model_name: str
    provider: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class TokenUsageUpdate(BaseModel):
    date: Optional[date_type] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    input_tokens: Optional[int] = Field(default=None, ge=0)
    output_tokens: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


class TokenUsageResponse(BaseModel):
    id: int
    date: date_type
    model_name: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    notes: Optional[str]
    user_id: Optional[int] = None
    source: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    records: list[TokenUsageResponse]
    total: int


class DailySummary(BaseModel):
    date: date_type
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    record_count: int

    model_config = {"from_attributes": True}


class ModelBreakdown(BaseModel):
    model_name: str
    provider: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    record_count: int

    model_config = {"from_attributes": True}


class ProviderBreakdown(BaseModel):
    provider: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    record_count: int

    model_config = {"from_attributes": True}


class Totals(BaseModel):
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    record_count: int


class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6, max_length=128)
    captcha_token: str


class UserLogin(BaseModel):
    email: str
    password: str
    captcha_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaptchaChallenge(BaseModel):
    token: str


# ── Leaderboard ────────────────────────────────────────────

class LeaderboardEntryResponse(BaseModel):
    id: int
    model_slug: str
    model_name: str
    provider: str
    organization: Optional[str] = None
    overall_score: Optional[float] = None
    rank_overall: Optional[int] = None
    score_gpqa: Optional[float] = None
    score_mmlu: Optional[float] = None
    score_mmlu_pro: Optional[float] = None
    score_math: Optional[float] = None
    score_humaneval: Optional[float] = None
    score_swebench: Optional[float] = None
    score_coding_arena: Optional[float] = None
    score_reasoning: Optional[float] = None
    score_coding: Optional[float] = None
    score_knowledge: Optional[float] = None
    score_tool_use: Optional[float] = None
    score_long_context: Optional[float] = None
    score_vision: Optional[float] = None
    category_math_score: Optional[float] = None
    category_writing_score: Optional[float] = None
    methodology_version: Optional[str] = None
    tokens_per_second: Optional[float] = None
    price_input: Optional[float] = None
    price_output: Optional[float] = None
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    knowledge_cutoff: Optional[str] = None
    modalities: Optional[str] = None
    tags: Optional[str] = None
    fetched_at: datetime
    # Modality-generic fields
    category: Optional[str] = None
    arena_rating: Optional[float] = None
    output_resolution: Optional[str] = None
    latency: Optional[float] = None

    model_config = {"from_attributes": True}


class LeaderboardPaginatedResponse(BaseModel):
    entries: list[LeaderboardEntryResponse]
    total: int


class LeaderboardSummary(BaseModel):
    total_models: int
    total_providers: int
    avg_overall_score: Optional[float] = None
    avg_price_input: Optional[float] = None
    avg_tokens_per_second: Optional[float] = None
    last_fetched_at: Optional[datetime] = None
    methodology_version: Optional[str] = None


# ── Email Sync ────────────────────────────────────────────

class EmailAccountCreate(BaseModel):
    provider_type: str  # "gmail_oauth" | "imap"
    email_address: str
    imap_server: Optional[str] = None
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    sync_interval_minutes: int = Field(default=60, ge=15, le=1440)
    monitored_providers: Optional[list[str]] = None


class EmailAccountUpdate(BaseModel):
    sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = Field(default=None, ge=15, le=1440)
    monitored_providers: Optional[list[str]] = None


class EmailAccountResponse(BaseModel):
    id: int
    email_address: str
    provider_type: str
    sync_enabled: bool
    sync_interval_minutes: int
    last_synced_at: Optional[datetime] = None
    monitored_providers: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncResultResponse(BaseModel):
    ok: bool
    emails_fetched: int = 0
    emails_parsed: int = 0
    records_created: int = 0
    errors: list[str] = []
    sync_log_id: int | None = None
    status: str = "completed"  # "running" | "success" | "error"


class SyncLogResponse(BaseModel):
    id: int
    email_account_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    emails_fetched: int
    emails_parsed: int
    records_created: int
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedSyncLogsResponse(BaseModel):
    logs: list[SyncLogResponse]
    total: int


class EmailAccountStatusItem(BaseModel):
    account_id: int
    email_address: str
    provider_type: str
    sync_enabled: bool
    last_synced_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None
    total_synced_emails: int = 0


class SyncStatusResponse(BaseModel):
    total_accounts: int = 0
    active_accounts: int = 0
    last_global_sync: Optional[datetime] = None
    total_synced_emails: int = 0
    total_synced_records: int = 0
    accounts: list[EmailAccountStatusItem] = []


class OAuthURLResponse(BaseModel):
    url: str


class IMAPTestRequest(BaseModel):
    imap_server: str
    imap_username: str
    imap_password: str


class IMAPTestResponse(BaseModel):
    ok: bool
    message: str = ""


class EmailPreviewItem(BaseModel):
    message_id: str
    subject: str
    from_addr: str
    date: datetime | None = None
    provider: str = "Unknown"
    model_name: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    parsed: bool = False
    body_snippet: str | None = None


class PreviewResponse(BaseModel):
    emails_fetched: int = 0
    emails_parsed: int = 0
    records_would_create: int = 0
    items: list[EmailPreviewItem] = []
