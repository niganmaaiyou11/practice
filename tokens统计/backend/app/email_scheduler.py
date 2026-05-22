from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def _sync_account_sync_wrapper(account_id: int):
    """Synchronous wrapper for async sync, called by APScheduler."""
    import asyncio
    from app.database import SessionLocal
    from app.email_sync import run_sync_for_account

    async def _run():
        db = SessionLocal()
        try:
            await run_sync_for_account(account_id, db)
        finally:
            db.close()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_run())
        loop.close()
    except Exception as e:
        logger.exception(f"Scheduled sync failed for account {account_id}: {e}")


def scan_and_sync_all():
    """Scan all enabled email accounts and sync those due for sync."""
    from app.database import SessionLocal
    from app.models import EmailAccount

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        accounts = db.query(EmailAccount).filter(EmailAccount.sync_enabled == True).all()

        for account in accounts:
            if account.last_synced_at:
                minutes_since = (now - account.last_synced_at).total_seconds() / 60
                if minutes_since < account.sync_interval_minutes:
                    continue
            _sync_account_sync_wrapper(account.id)
    finally:
        db.close()


def start_scheduler():
    global scheduler
    if scheduler is not None:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        scan_and_sync_all,
        trigger="interval",
        minutes=15,
        id="email_sync_scanner",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Email sync scheduler started")


def stop_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Email sync scheduler stopped")
