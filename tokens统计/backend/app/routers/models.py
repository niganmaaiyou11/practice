from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import User

router = APIRouter()

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "models.json"
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"

_cache = None


def _load_cache():
    global _cache
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _cache = {"providers": [], "updated_at": None, "source": "fallback"}


_load_cache()


@router.get("/models")
def get_models(user: User = Depends(get_current_user)):
    return _cache


@router.get("/models/providers")
def get_providers(user: User = Depends(get_current_user)):
    return [p["name"] for p in _cache.get("providers", [])]


@router.post("/models/sync")
def sync_models(user: User = Depends(get_current_user)):
    """Trigger a sync from model sources and return the updated registry."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "sync_models.py")],
            capture_output=True, text=True, timeout=120,
            cwd=str(SCRIPTS_DIR.parent),
        )
        _load_cache()
        provider_count = len(_cache.get("providers", []))
        model_count = sum(len(p.get("models", [])) for p in _cache.get("providers", []))
        return {
            "ok": True,
            "providers": provider_count,
            "models": model_count,
            "updated_at": _cache.get("updated_at"),
            "output": result.stdout.strip().split("\n")[-3:] if result.stdout else [],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "detail": "Sync timed out after 120s"}
    except Exception as e:
        return {"ok": False, "detail": str(e)}
