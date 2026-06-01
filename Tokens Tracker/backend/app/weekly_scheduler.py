from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
scheduler: BackgroundScheduler | None = None


def refresh_weekly_news():
    from app.database import SessionLocal
    from app.weekly_news import fetch_weekly_news, publish_weekly_items

    async def _run():
        items, statuses = await fetch_weekly_news()
        db = SessionLocal()
        try:
            count = publish_weekly_items(db, items)
            logger.info("Weekly news refresh published %s new items", count)

            # Generate notifications for new items
            if count > 0:
                _create_weekly_notifications(db, count)

        finally:
            db.close()

        # Log summary
        ok = sum(1 for s in statuses if s.ok)
        failed = sum(1 for s in statuses if not s.ok)
        if failed:
            for s in statuses:
                if not s.ok:
                    logger.warning("  Source failed: %s — %s", s.name, s.error)
        logger.info("Feed summary: %d OK, %d failed, %d new items published", ok, failed, count)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_run())
        loop.close()
    except Exception as e:
        logger.exception("Weekly news refresh failed: %s", e)


def _create_weekly_notifications(db, new_count: int):
    """Create in-app notifications for all users when new weekly items are published."""
    from app.models import Notification, User
    try:
        users = db.query(User).all()
        for user in users:
            notification = Notification(
                user_id=user.id,
                title="AI 周报更新",
                message=f"本周 AI 周报已更新，新增 {new_count} 条资讯，点击查看最新动态。",
                type="weekly",
                link="/weekly",
                is_read=False,
            )
            db.add(notification)
        db.commit()
        logger.info("Created weekly notifications for %d users (%d new items)", len(users), new_count)
    except Exception as e:
        db.rollback()
        logger.warning("Failed to create weekly notifications: %s", e)


def start_scheduler():
    global scheduler
    if scheduler is not None:
        return
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        refresh_weekly_news,
        trigger="interval",
        hours=6,
        id="weekly_news_refresh",
        replace_existing=True,
    )
    scheduler.start()
    refresh_weekly_news()
    logger.info("Weekly news scheduler started")


def stop_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Weekly news scheduler stopped")
