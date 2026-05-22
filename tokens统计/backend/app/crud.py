from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import func, and_, desc, asc
from sqlalchemy.orm import Session
from app.models import TokenUsage, LeaderboardEntry, EmailAccount, SyncedEmail, SyncLog
from app.schemas import TokenUsageCreate, TokenUsageUpdate


def get_records(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
    model_name: str | None = None,
) -> tuple[list[TokenUsage], int]:
    query = db.query(TokenUsage)
    filters = []

    if start_date:
        filters.append(TokenUsage.date >= start_date)
    if end_date:
        filters.append(TokenUsage.date <= end_date)
    if provider:
        filters.append(TokenUsage.provider == provider)
    if model_name:
        filters.append(TokenUsage.model_name == model_name)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    records = query.order_by(TokenUsage.date.desc(), TokenUsage.created_at.desc()).offset(skip).limit(limit).all()
    return records, total


def get_record(db: Session, record_id: int) -> TokenUsage | None:
    return db.query(TokenUsage).filter(TokenUsage.id == record_id).first()


def create_record(db: Session, data: TokenUsageCreate, user_id: int = 1) -> TokenUsage:
    record = TokenUsage(
        date=data.date,
        model_name=data.model_name,
        provider=data.provider,
        input_tokens=data.input_tokens,
        output_tokens=data.output_tokens,
        total_tokens=data.input_tokens + data.output_tokens,
        notes=data.notes,
        user_id=user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record_id: int, data: TokenUsageUpdate) -> TokenUsage | None:
    record = db.query(TokenUsage).filter(TokenUsage.id == record_id).first()
    if not record:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    # Recompute total_tokens when input or output changes
    if "input_tokens" in update_data or "output_tokens" in update_data:
        record.total_tokens = record.input_tokens + record.output_tokens

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int) -> bool:
    record = db.query(TokenUsage).filter(TokenUsage.id == record_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def _build_filters(start_date, end_date, provider):
    filters = []
    if start_date:
        filters.append(TokenUsage.date >= start_date)
    if end_date:
        filters.append(TokenUsage.date <= end_date)
    if provider:
        filters.append(TokenUsage.provider == provider)
    return and_(*filters) if filters else None


def get_daily_summary(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
) -> list[dict]:
    f = _build_filters(start_date, end_date, provider)
    query = db.query(
        TokenUsage.date,
        func.sum(TokenUsage.input_tokens).label("total_input_tokens"),
        func.sum(TokenUsage.output_tokens).label("total_output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens"),
        func.count(TokenUsage.id).label("record_count"),
    )
    if f is not None:
        query = query.filter(f)
    rows = query.group_by(TokenUsage.date).order_by(TokenUsage.date.asc()).all()
    return [dict(row._mapping) for row in rows]


def get_model_breakdown(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
) -> list[dict]:
    f = _build_filters(start_date, end_date, provider)
    query = db.query(
        TokenUsage.model_name,
        TokenUsage.provider,
        func.sum(TokenUsage.input_tokens).label("total_input_tokens"),
        func.sum(TokenUsage.output_tokens).label("total_output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens"),
        func.count(TokenUsage.id).label("record_count"),
    )
    if f is not None:
        query = query.filter(f)
    rows = query.group_by(TokenUsage.model_name).order_by(func.sum(TokenUsage.total_tokens).desc()).all()
    return [dict(row._mapping) for row in rows]


def get_provider_breakdown(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
) -> list[dict]:
    f = _build_filters(start_date, end_date, provider)
    query = db.query(
        TokenUsage.provider,
        func.sum(TokenUsage.input_tokens).label("total_input_tokens"),
        func.sum(TokenUsage.output_tokens).label("total_output_tokens"),
        func.sum(TokenUsage.total_tokens).label("total_tokens"),
        func.count(TokenUsage.id).label("record_count"),
    )
    if f is not None:
        query = query.filter(f)
    rows = query.group_by(TokenUsage.provider).order_by(func.sum(TokenUsage.total_tokens).desc()).all()
    return [dict(row._mapping) for row in rows]


def get_totals(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str | None = None,
) -> dict:
    f = _build_filters(start_date, end_date, provider)
    query = db.query(
        func.coalesce(func.sum(TokenUsage.input_tokens), 0).label("total_input_tokens"),
        func.coalesce(func.sum(TokenUsage.output_tokens), 0).label("total_output_tokens"),
        func.coalesce(func.sum(TokenUsage.total_tokens), 0).label("total_tokens"),
        func.count(TokenUsage.id).label("record_count"),
    )
    if f is not None:
        query = query.filter(f)
    row = query.first()
    return dict(row._mapping)


# ── Leaderboard ────────────────────────────────────────────

LEADERBOARD_SORT_COLS = {
    "overall_score": LeaderboardEntry.overall_score,
    "tokens_per_second": LeaderboardEntry.tokens_per_second,
    "price_input": LeaderboardEntry.price_input,
    "price_output": LeaderboardEntry.price_output,
    "context_window": LeaderboardEntry.context_window,
    "score_gpqa": LeaderboardEntry.score_gpqa,
    "score_mmlu": LeaderboardEntry.score_mmlu,
    "score_math": LeaderboardEntry.score_math,
    "score_humaneval": LeaderboardEntry.score_humaneval,
    "score_swebench": LeaderboardEntry.score_swebench,
    "rank_overall": LeaderboardEntry.rank_overall,
    "model_name": LeaderboardEntry.model_name,
    "score_reasoning": LeaderboardEntry.score_reasoning,
    "score_coding": LeaderboardEntry.score_coding,
    "score_knowledge": LeaderboardEntry.score_knowledge,
    "score_tool_use": LeaderboardEntry.score_tool_use,
    "score_long_context": LeaderboardEntry.score_long_context,
    "score_vision": LeaderboardEntry.score_vision,
    "category_math_score": LeaderboardEntry.category_math_score,
    "category_writing_score": LeaderboardEntry.category_writing_score,
    "arena_rating": LeaderboardEntry.arena_rating,
    "latency": LeaderboardEntry.latency,
}


def get_leaderboard_entries(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    provider: str | None = None,
    search: str | None = None,
    sort_by: str = "overall_score",
    sort_dir: str = "desc",
    organizations: list[str] | None = None,
    tags: str | None = None,
    modality: str | None = None,
) -> tuple[list[LeaderboardEntry], int]:
    query = db.query(LeaderboardEntry)
    if provider:
        query = query.filter(LeaderboardEntry.provider == provider)
    if organizations:
        query = query.filter(LeaderboardEntry.organization.in_(organizations))
    if tags:
        for tag in [t.strip() for t in tags.split(",") if t.strip()]:
            query = query.filter(LeaderboardEntry.tags.ilike(f"%{tag}%"))
    if modality:
        category_map = {"text": "llm", "image": "image", "video": "video", "tts": "tts", "stt": "stt"}
        target = category_map.get(modality)
        if target:
            if target == "llm":
                query = query.filter(
                    (LeaderboardEntry.category == target) | (LeaderboardEntry.category.is_(None))
                )
            else:
                query = query.filter(LeaderboardEntry.category == target)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            LeaderboardEntry.model_name.ilike(pattern)
            | LeaderboardEntry.provider.ilike(pattern)
        )
    total = query.count()
    col = LEADERBOARD_SORT_COLS.get(sort_by, LeaderboardEntry.overall_score)
    order_fn = desc if sort_dir == "desc" else asc
    # Put NULLs last — must wrap the direction first, then nullslast() (SQLite syntax: "col DESC NULLS LAST")
    entries = query.order_by(order_fn(col).nullslast()).offset(skip).limit(limit).all()
    return entries, total


def get_leaderboard_entry(db: Session, entry_id: int) -> LeaderboardEntry | None:
    return db.query(LeaderboardEntry).filter(LeaderboardEntry.id == entry_id).first()


def get_leaderboard_providers(db: Session) -> list[str]:
    rows = db.query(LeaderboardEntry.provider).distinct().order_by(LeaderboardEntry.provider).all()
    return [r[0] for r in rows]


def get_leaderboard_summary(db: Session, modality: str | None = None) -> dict:
    query = db.query(
        func.count(LeaderboardEntry.id).label("total_models"),
        func.count(func.distinct(LeaderboardEntry.provider)).label("total_providers"),
        func.avg(LeaderboardEntry.overall_score).label("avg_overall_score"),
        func.avg(LeaderboardEntry.price_input).label("avg_price_input"),
        func.avg(LeaderboardEntry.tokens_per_second).label("avg_tokens_per_second"),
        func.max(LeaderboardEntry.fetched_at).label("last_fetched_at"),
        func.max(LeaderboardEntry.methodology_version).label("methodology_version"),
    )
    if modality:
        category_map = {"text": "llm", "image": "image", "video": "video", "tts": "tts", "stt": "stt"}
        target = category_map.get(modality)
        if target:
            if target == "llm":
                query = query.filter(
                    (LeaderboardEntry.category == target) | (LeaderboardEntry.category.is_(None))
                )
            else:
                query = query.filter(LeaderboardEntry.category == target)
    row = query.first()
    return dict(row._mapping)


def upsert_leaderboard_entry(db: Session, data: dict) -> LeaderboardEntry:
    existing = db.query(LeaderboardEntry).filter(
        LeaderboardEntry.model_slug == data["model_slug"]
    ).first()
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    entry = LeaderboardEntry(**data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_leaderboard_top(db: Session, limit: int = 5, modality: str | None = None) -> list[LeaderboardEntry]:
    query = db.query(LeaderboardEntry).filter(LeaderboardEntry.overall_score.isnot(None))
    if modality:
        category_map = {"text": "llm", "image": "image", "video": "video", "tts": "tts", "stt": "stt"}
        target = category_map.get(modality)
        if target:
            if target == "llm":
                query = query.filter(
                    (LeaderboardEntry.category == target) | (LeaderboardEntry.category.is_(None))
                )
            else:
                query = query.filter(LeaderboardEntry.category == target)
    return (
        query.order_by(desc(LeaderboardEntry.overall_score))
        .limit(limit)
        .all()
    )


def get_last_fetched_at(db: Session) -> datetime | None:
    row = db.query(func.max(LeaderboardEntry.fetched_at)).first()
    return row[0] if row else None


# ── Model Tag Derivation ─────────────────────────────────────

# Known open-source providers / organizations
OPEN_SOURCE_ORGS = {
    "Meta", "Mistral", "DeepSeek", "Alibaba", "Qwen", "ByteDance",
    "01.AI", "Baichuan", "MiniMax", "StepFun", "Zhipu AI",
    "Moonshot AI", "Tencent", "Baidu", "iFlytek", "OpenBMB",
    "SenseTime", "LongCat", "MiMo", "Muse", "HiDream",
    "Nous Research", "Allen AI", "EleutherAI", "Stability AI",
    "Microsoft", "TII", "Upstage", "LG", "Databricks", "Snowflake",
}

# Known proprietary providers
PROPRIETARY_ORGS = {
    "OpenAI", "Anthropic", "Google", "xAI", "Cohere", "AI21",
    "Reka", "Adept",
}


def derive_model_tags(entry: LeaderboardEntry) -> list[str]:
    """Derive category tags from a model's existing attributes."""
    tags: list[str] = []

    org = (entry.organization or "").strip()
    provider = (entry.provider or "").strip().lower()

    # License type
    if org in OPEN_SOURCE_ORGS:
        tags.append("open-source")
    elif org in PROPRIETARY_ORGS:
        tags.append("proprietary")
    else:
        # Fallback: check by known provider slugs
        open_src_providers = {"meta", "mistral", "deepseek", "alibaba", "qwen",
                              "bytedance", "zhipu-ai", "moonshot", "minimax",
                              "stepfun", "01-ai", "baichuan", "baidu", "iflytek",
                              "tencent", "nous-research", "allenai", "eleutherai",
                              "microsoft", "tii", "upstage", "databricks"}
        prop_providers = {"openai", "anthropic", "google", "xai", "x-ai",
                          "cohere", "ai21", "reka", "adept"}
        if provider in open_src_providers or org in open_src_providers:
            tags.append("open-source")
        elif provider in prop_providers or org in prop_providers:
            tags.append("proprietary")

    # Multimodal: check modalities field
    modalities = (entry.modalities or "").lower()
    if any(m in modalities for m in ["vision", "image", "video", "audio", "multimodal"]):
        tags.append("multimodal")

    # Performance-based categories (top ~30% in each dimension)
    if entry.score_coding is not None and entry.score_coding >= 0.60:
        tags.append("coding")
    if entry.score_reasoning is not None and entry.score_reasoning >= 0.60:
        tags.append("reasoning")
    if entry.score_tool_use is not None and entry.score_tool_use >= 0.50:
        tags.append("agentic")

    # Cost efficient: below median price
    if entry.price_input is not None and entry.price_input <= 2.0:
        tags.append("cost-efficient")

    # Long context: 128K+
    if entry.context_window is not None and entry.context_window >= 128000:
        tags.append("long-context")

    return tags


def populate_missing_tags(db: Session) -> int:
    """Fill in tags for models that don't have them yet. Returns count updated."""
    entries = db.query(LeaderboardEntry).filter(
        LeaderboardEntry.tags.is_(None)
    ).all()
    count = 0
    for entry in entries:
        derived = derive_model_tags(entry)
        if derived:
            entry.tags = ",".join(derived)
            count += 1
    db.commit()
    return count


# ── Email Account CRUD ──────────────────────────────

def create_email_account(db: Session, user_id: int, email_address: str, provider_type: str,
                         access_token_encrypted: str | None = None,
                         refresh_token_encrypted: str | None = None,
                         token_expires_at: datetime | None = None,
                         imap_server: str | None = None,
                         imap_username: str | None = None,
                         imap_password_encrypted: str | None = None,
                         sync_interval_minutes: int = 60,
                         monitored_providers: str | None = None) -> EmailAccount:
    account = EmailAccount(
        user_id=user_id,
        email_address=email_address,
        provider_type=provider_type,
        access_token_encrypted=access_token_encrypted,
        refresh_token_encrypted=refresh_token_encrypted,
        token_expires_at=token_expires_at,
        imap_server=imap_server,
        imap_username=imap_username,
        imap_password_encrypted=imap_password_encrypted,
        sync_interval_minutes=sync_interval_minutes,
        monitored_providers=monitored_providers,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_email_accounts(db: Session, user_id: int) -> list[EmailAccount]:
    return db.query(EmailAccount).filter(EmailAccount.user_id == user_id).all()


def get_email_account(db: Session, account_id: int, user_id: int) -> EmailAccount | None:
    return db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == user_id,
    ).first()


def update_email_account(db: Session, account_id: int, user_id: int, **kwargs) -> EmailAccount | None:
    account = get_email_account(db, account_id, user_id)
    if not account:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(account, key):
            setattr(account, key, value)
    account.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(account)
    return account


def delete_email_account(db: Session, account_id: int, user_id: int) -> bool:
    account = get_email_account(db, account_id, user_id)
    if not account:
        return False
    # Delete related synced_emails and sync_logs first
    db.query(SyncedEmail).filter(SyncedEmail.email_account_id == account.id).delete()
    db.query(SyncLog).filter(SyncLog.email_account_id == account.id).delete()
    db.delete(account)
    db.commit()
    return True


def get_sync_logs(db: Session, user_id: int, skip: int = 0, limit: int = 20,
                  account_id: int | None = None) -> tuple[list[SyncLog], int]:
    query = db.query(SyncLog).join(EmailAccount).filter(EmailAccount.user_id == user_id)
    if account_id:
        query = query.filter(SyncLog.email_account_id == account_id)
    total = query.count()
    logs = query.order_by(SyncLog.started_at.desc()).offset(skip).limit(limit).all()
    return logs, total


def get_sync_status(db: Session, user_id: int) -> dict:
    accounts = get_email_accounts(db, user_id)
    total_accounts = len(accounts)
    active_accounts = sum(1 for a in accounts if a.sync_enabled)
    last_global = max((a.last_synced_at for a in accounts if a.last_synced_at), default=None)

    total_emails = 0
    total_records = 0
    items = []
    for a in accounts:
        synced_count = db.query(func.count(SyncedEmail.id)).filter(
            SyncedEmail.email_account_id == a.id
        ).scalar() or 0
        total_emails += synced_count

        record_count = db.query(func.count(SyncedEmail.id)).filter(
            SyncedEmail.email_account_id == a.id,
            SyncedEmail.token_usage_id.isnot(None),
        ).scalar() or 0
        total_records += record_count

        last_log = db.query(SyncLog).filter(
            SyncLog.email_account_id == a.id
        ).order_by(SyncLog.started_at.desc()).first()

        items.append({
            "account_id": a.id,
            "email_address": a.email_address,
            "provider_type": a.provider_type,
            "sync_enabled": a.sync_enabled,
            "last_synced_at": a.last_synced_at,
            "last_sync_status": last_log.status if last_log else None,
            "total_synced_emails": synced_count,
        })

    return {
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "last_global_sync": last_global,
        "total_synced_emails": total_emails,
        "total_synced_records": total_records,
        "accounts": items,
    }
