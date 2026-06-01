from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import SessionLocal
from app.models import User, WeeklyNewsItem
from app.schemas import WeeklyNewsItemResponse, WeeklyNewsResponse
from app.weekly_news import weekly_item_to_dict, get_refresh_status

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _highlights(items: list[WeeklyNewsItem]) -> list[str]:
    highlights = [item.summary for item in items[:3]]
    if highlights:
        return highlights
    return [
        "AI Weekly is waiting for the first automatic news refresh.",
        "The backend refreshes sources automatically and publishes new items when available.",
        "Check back after the next scheduled refresh for model, industry, open-source, tool, and China AI updates.",
    ]


@router.get("/weekly", response_model=WeeklyNewsResponse)
def weekly_news(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(WeeklyNewsItem)
        .filter(WeeklyNewsItem.is_published == True)
        .order_by(WeeklyNewsItem.published_at.desc())
        .limit(50)
        .all()
    )
    issue_date = items[0].published_at.date() if items else date.today()
    return WeeklyNewsResponse(
        issue_date=issue_date,
        highlights=_highlights(items),
        items=[WeeklyNewsItemResponse(**weekly_item_to_dict(item)) for item in items],
    )


@router.get("/weekly/{slug}", response_model=WeeklyNewsItemResponse)
def weekly_news_item(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(WeeklyNewsItem)
        .filter(WeeklyNewsItem.slug == slug, WeeklyNewsItem.is_published == True)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Weekly news item not found")
    return WeeklyNewsItemResponse(**weekly_item_to_dict(item))


@router.post("/weekly/refresh")
async def trigger_refresh(
    current_user: User = Depends(get_current_user),
):
    """Manually trigger a weekly news refresh."""
    from app.weekly_news import fetch_weekly_news, publish_weekly_items
    from app.weekly_scheduler import _create_weekly_notifications
    from app.database import SessionLocal

    items, statuses = await fetch_weekly_news()
    count = 0
    db = SessionLocal()
    try:
        count = publish_weekly_items(db, items)
        if count > 0:
            _create_weekly_notifications(db, count)
    finally:
        db.close()

    ok = sum(1 for s in statuses if s.ok)
    failed = sum(1 for s in statuses if not s.ok)
    return {
        "ok": True,
        "new_items": count,
        "sources_ok": ok,
        "sources_failed": failed,
        "total_fetched": len(items),
    }


@router.get("/weekly-status")
def weekly_status(
    current_user: User = Depends(get_current_user),
):
    """Return feed status and last refresh info."""
    status = get_refresh_status()
    return status
