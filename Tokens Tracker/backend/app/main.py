import os
from pathlib import Path

# Load .env file before anything else
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base, run_migrations
from app.routers import auth, token_records, models, leaderboard, email, weekly, notifications

Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(title="AI Token Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(token_records.router, prefix="/api")
app.include_router(models.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(email.router, prefix="/api")
app.include_router(weekly.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")


@app.on_event("startup")
def startup_leaderboard_seed():
    """Auto-fill leaderboard table on first launch if empty, and populate tags (non-blocking)."""
    from app.database import SessionLocal
    from app.models import LeaderboardEntry
    from app import crud
    import subprocess, os, sys
    db = SessionLocal()
    try:
        count = db.query(LeaderboardEntry).count()
        if count > 0:
            crud.populate_missing_tags(db)
    finally:
        db.close()
    if count == 0:
        script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scripts", "scrape_llm_stats.py",
        )
        subprocess.Popen(
            [sys.executable, script],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

    # Start email sync scheduler
    try:
        from app.email_scheduler import start_scheduler
        start_scheduler()
    except Exception:
        pass

    # Start automatic AI Weekly refresh and publish scheduler
    try:
        from app.weekly_scheduler import start_scheduler as start_weekly_scheduler
        start_weekly_scheduler()
    except Exception:
        pass


@app.on_event("shutdown")
def shutdown_scheduler():
    try:
        from app.email_scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    try:
        from app.weekly_scheduler import stop_scheduler as stop_weekly_scheduler
        stop_weekly_scheduler()
    except Exception:
        pass


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
