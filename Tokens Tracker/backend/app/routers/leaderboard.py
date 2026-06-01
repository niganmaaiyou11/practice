from __future__ import annotations
import re
import subprocess
import os
import sys
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
from app.auth import get_current_user
from app.models import User
from app.schemas import (
    LeaderboardEntryResponse,
    LeaderboardPaginatedResponse,
    LeaderboardSummary,
)

router = APIRouter()

CHINESE_ORGANIZATIONS = [
    "DeepSeek", "Alibaba", "Zhipu AI", "Moonshot AI", "ByteDance",
    "MiniMax", "StepFun", "Baidu", "iFlytek", "Tencent", "01.AI",
    "Baichuan", "SenseTime", "Hunyuan", "Kling", "HiDream",
    "Xiaomi", "MiMo", "OpenBMB", "Muse", "LongCat",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/leaderboard/models", response_model=LeaderboardPaginatedResponse)
def list_models(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    provider: str | None = None,
    search: str | None = None,
    sort_by: str = Query(default="overall_score"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    china_only: bool = Query(default=False),
    organizations: str | None = Query(default=None, description="Comma-separated organization names"),
    tags: str | None = Query(default=None, description="Comma-separated tag filter (e.g. 'open-source,multimodal')"),
    modality: str | None = Query(default=None, description="Modality filter: text, image, video, audio, tts, stt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_list: list[str] | None = None
    if china_only:
        org_list = CHINESE_ORGANIZATIONS
    elif organizations:
        org_list = [o.strip() for o in organizations.split(",") if o.strip()]
    entries, total = crud.get_leaderboard_entries(db, skip, limit, provider, search, sort_by, sort_dir, org_list, tags, modality)
    return LeaderboardPaginatedResponse(
        entries=[LeaderboardEntryResponse.model_validate(e) for e in entries],
        total=total,
    )


@router.get("/leaderboard/models/{entry_id}", response_model=LeaderboardEntryResponse)
def get_model(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = crud.get_leaderboard_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Model not found")
    return LeaderboardEntryResponse.model_validate(entry)


@router.get("/leaderboard/top", response_model=list[LeaderboardEntryResponse])
def top_models(
    limit: int = Query(default=5, ge=1, le=20),
    modality: str | None = Query(default=None, description="Modality filter: text, image, video, tts, stt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entries = crud.get_leaderboard_top(db, limit, modality)
    return [LeaderboardEntryResponse.model_validate(e) for e in entries]


@router.get("/leaderboard/summary", response_model=LeaderboardSummary)
def summary(
    modality: str | None = Query(default=None, description="Modality filter: text, image, video, tts, stt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return LeaderboardSummary(**crud.get_leaderboard_summary(db, modality))


@router.get("/leaderboard/public/summary", response_model=LeaderboardSummary)
def public_summary(
    modality: str | None = Query(default=None, description="Modality filter: text, image, video, tts, stt"),
    db: Session = Depends(get_db),
):
    return LeaderboardSummary(**crud.get_leaderboard_summary(db, modality))


@router.get("/leaderboard/providers")
def list_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_leaderboard_providers(db)


@router.post("/leaderboard/sync")
def sync_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Calculate paths relative to this file:
    # __file__ → backend/app/routers/leaderboard.py
    # dirname ×3 → backend/
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script = os.path.join(backend_root, "scripts", "scrape_llm_stats.py")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, timeout=120,
            cwd=backend_root,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            m = re.search(r'(\d+)\s*models?\s*upserted(?:\s*from\s*([\w+-]+))?', output)
            count = int(m.group(1)) if m else 0
            source = m.group(2) if m and m.group(2) else None
            tag_count = crud.populate_missing_tags(db)
            summary_data = crud.get_leaderboard_summary(db)
            providers = crud.get_leaderboard_providers(db)
            last_fetched_at = summary_data.get("last_fetched_at")
            return {
                "ok": True,
                "output": f"Synced {count} models. Auto-tagged {tag_count} models.",
                "models": summary_data.get("total_models") or count,
                "providers": len(providers),
                "last_fetched_at": last_fetched_at.isoformat() if last_fetched_at else None,
                "source": source,
            }
        return {
            "ok": False,
            "output": result.stderr.strip() or result.stdout.strip() or "Sync failed",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Sync timed out (120s)"}
    except Exception as e:
        return {"ok": False, "output": str(e)}


@router.get("/leaderboard/last-updated")
def last_updated(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ts = crud.get_last_fetched_at(db)
    return {"last_fetched_at": ts.isoformat() if ts else None}


@router.post("/leaderboard/populate-tags")
def populate_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = crud.populate_missing_tags(db)
    return {"ok": True, "count": count}
