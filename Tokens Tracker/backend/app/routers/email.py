from __future__ import annotations
import json
import asyncio
import threading

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import crud
from app.auth import get_current_user
from app.models import User
from app.email_auth import (
    build_oauth_url, decode_state, exchange_code, get_user_email,
    encrypt_token, test_imap_connection,
)
from app.email_sync import run_sync_for_account
from app.schemas import (
    EmailAccountCreate, EmailAccountUpdate, EmailAccountResponse,
    SyncResultResponse, SyncLogResponse, PaginatedSyncLogsResponse,
    SyncStatusResponse, OAuthURLResponse, IMAPTestRequest, IMAPTestResponse,
    EmailAccountStatusItem, PreviewResponse, EmailPreviewItem,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── OAuth ──────────────────────────────────────────

@router.get("/email/oauth-url", response_model=OAuthURLResponse)
def get_oauth_url(current_user: User = Depends(get_current_user)):
    url = build_oauth_url(current_user.id)
    return OAuthURLResponse(url=url)


@router.get("/email/oauth-callback")
def oauth_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Google OAuth callback. Returns HTML that posts result to parent window."""
    try:
        state_data = decode_state(state)
        user_id = state_data["user_id"]
    except Exception:
        return HTMLResponse(content="<script>window.close()</script>")

    async def _exchange():
        return await exchange_code(code)

    try:
        loop = asyncio.new_event_loop()
        token_data = loop.run_until_complete(_exchange())
        loop.close()

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token", "")

        # Get user email
        loop2 = asyncio.new_event_loop()
        email_addr = loop2.run_until_complete(get_user_email(access_token))
        loop2.close()

        # Check if account already exists for this user
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.id == user_id).first()
            if not existing:
                return HTMLResponse(content="<script>window.close()</script>")

            # Check for existing email account
            from app.models import EmailAccount
            ea = db.query(EmailAccount).filter(
                EmailAccount.user_id == user_id,
                EmailAccount.email_address == email_addr,
            ).first()

            encrypted_access = encrypt_token(access_token)
            encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None
            from datetime import datetime, timezone, timedelta
            expires = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))

            if ea:
                ea.access_token_encrypted = encrypted_access
                ea.refresh_token_encrypted = encrypted_refresh or ea.refresh_token_encrypted
                ea.token_expires_at = expires
                db.commit()
            else:
                crud.create_email_account(
                    db, user_id, email_addr, "gmail_oauth",
                    access_token_encrypted=encrypted_access,
                    refresh_token_encrypted=encrypted_refresh,
                    token_expires_at=expires,
                )
        finally:
            db.close()

        return HTMLResponse(content=f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<script>
if (window.opener) {{
    window.opener.postMessage({{type: 'gmail-oauth-success', email: '{email_addr}'}}, '*');
    window.close();
}} else {{
    window.close();
}}
</script>
<p>Authorization successful. You may close this window.</p>
</body></html>""")
    except Exception as e:
        return HTMLResponse(content=f"""<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>
<script>
if (window.opener) {{
    window.opener.postMessage({{type: 'gmail-oauth-error', error: '{str(e)}'}}, '*');
}}
window.close();
</script>
<p>Authorization failed: {str(e)}. You may close this window.</p>
</body></html>""")


# ── Email Accounts CRUD ────────────────────────────

@router.get("/email/accounts", response_model=list[EmailAccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_email_accounts(db, current_user.id)


@router.post("/email/accounts", response_model=EmailAccountResponse, status_code=201)
def create_account(
    data: EmailAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.provider_type == "imap":
        if not data.imap_server or not data.imap_username or not data.imap_password:
            raise HTTPException(status_code=400, detail="IMAP server, username, and password are required")

        from app.email_auth import encrypt_token
        encrypted_pwd = encrypt_token(data.imap_password)
    else:
        encrypted_pwd = None

    monitored = json.dumps(data.monitored_providers) if data.monitored_providers else None

    return crud.create_email_account(
        db, current_user.id, data.email_address, data.provider_type,
        imap_server=data.imap_server,
        imap_username=data.imap_username,
        imap_password_encrypted=encrypted_pwd,
        sync_interval_minutes=data.sync_interval_minutes,
        monitored_providers=monitored,
    )


@router.put("/email/accounts/{account_id}", response_model=EmailAccountResponse)
def update_account(
    account_id: int,
    data: EmailAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kwargs = data.model_dump(exclude_unset=True)
    if "monitored_providers" in kwargs and kwargs["monitored_providers"] is not None:
        kwargs["monitored_providers"] = json.dumps(kwargs["monitored_providers"])
    account = crud.update_email_account(db, account_id, current_user.id, **kwargs)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")
    return account


@router.delete("/email/accounts/{account_id}", status_code=204)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = crud.delete_email_account(db, account_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Email account not found")


# ── Sync ───────────────────────────────────────────

@router.post("/email/accounts/{account_id}/sync", response_model=SyncResultResponse)
def trigger_sync(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = crud.get_email_account(db, account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    # Create a sync log entry immediately
    from datetime import datetime, timezone
    from app.models import SyncLog

    sync_log = SyncLog(
        email_account_id=account.id,
        started_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(sync_log)
    db.commit()
    db.refresh(sync_log)
    log_id = sync_log.id

    def _bg_sync():
        bg_db = SessionLocal()
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(run_sync_for_account(account_id, bg_db, sync_log_id=log_id))
            loop.close()
        finally:
            bg_db.close()

    t = threading.Thread(target=_bg_sync, daemon=True)
    t.start()

    return SyncResultResponse(
        ok=True,
        sync_log_id=log_id,
        status="running",
    )


# ── Preview / Dry-Run ────────────────────────────

@router.post("/email/accounts/{account_id}/preview", response_model=PreviewResponse)
def preview_sync(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch emails and show what would be synced, without creating any records."""
    from app.schemas import PreviewResponse, EmailPreviewItem
    from app.email_fetcher import fetch_messages, PROVIDER_TO_DOMAINS
    from app.email_parser import get_parser_for_sender
    import json
    from datetime import datetime as dt, timedelta, timezone as tz

    account = crud.get_email_account(db, account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    monitored = None
    if account.monitored_providers:
        try:
            monitored = json.loads(account.monitored_providers)
        except json.JSONDecodeError:
            pass

    since = account.last_synced_at or (dt.now(tz.utc) - timedelta(days=30))

    async def _run():
        return await fetch_messages(account, since=since, monitored_providers=monitored)

    loop = asyncio.new_event_loop()
    emails = loop.run_until_complete(_run())
    loop.close()

    items: list[EmailPreviewItem] = []
    parsed_count = 0
    would_create = 0

    for email_data in emails:
        parser = get_parser_for_sender(email_data.get("from", ""))
        parsed = parser.parse(email_data) if parser else None

        item = EmailPreviewItem(
            message_id=email_data["message_id"][:50],
            subject=email_data.get("subject", "")[:200],
            from_addr=email_data.get("from", ""),
            date=email_data.get("date"),
            body_snippet=(email_data.get("body_text", "") or "")[:300] if not parsed else None,
        )

        if parsed:
            item.parsed = True
            item.provider = parsed.provider
            item.model_name = parsed.model_name
            item.input_tokens = parsed.input_tokens
            item.output_tokens = parsed.output_tokens
            parsed_count += 1
            if parsed.input_tokens or parsed.output_tokens:
                would_create += 1 + len(parsed.all_models) - 1 if parsed.all_models else 0

        items.append(item)

    return PreviewResponse(
        emails_fetched=len(emails),
        emails_parsed=parsed_count,
        records_would_create=max(0, would_create),
        items=items,
    )


# ── Sync Logs ──────────────────────────────────────

@router.get("/email/sync-logs", response_model=PaginatedSyncLogsResponse)
def list_sync_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    account_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs, total = crud.get_sync_logs(db, current_user.id, skip, limit, account_id)
    return PaginatedSyncLogsResponse(
        logs=[SyncLogResponse.model_validate(l) for l in logs],
        total=total,
    )


@router.get("/email/sync-status", response_model=SyncStatusResponse)
def sync_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    status = crud.get_sync_status(db, current_user.id)
    return SyncStatusResponse(
        total_accounts=status["total_accounts"],
        active_accounts=status["active_accounts"],
        last_global_sync=status["last_global_sync"],
        total_synced_emails=status["total_synced_emails"],
        total_synced_records=status["total_synced_records"],
        accounts=[EmailAccountStatusItem(**a) for a in status["accounts"]],
    )


# ── IMAP Test ──────────────────────────────────────

@router.post("/email/test-imap", response_model=IMAPTestResponse)
async def test_imap(
    data: IMAPTestRequest,
    current_user: User = Depends(get_current_user),
):
    ok, message = await test_imap_connection(data.imap_server, data.imap_username, data.imap_password)
    return IMAPTestResponse(ok=ok, message=message)
