from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./token_tracker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def run_migrations():
    """Add missing columns to existing tables (safe for SQLite)."""
    import sqlite3

    db_path = engine.url.database
    if not db_path or not isinstance(db_path, str):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # leaderboard_entries: add llm-stats.com v1.0 6-axis score columns
        lb_cols = {r[1] for r in cur.execute("PRAGMA table_info(leaderboard_entries)")}
        new_cols = [
            ("score_reasoning", "FLOAT"),
            ("score_coding", "FLOAT"),
            ("score_knowledge", "FLOAT"),
            ("score_tool_use", "FLOAT"),
            ("score_long_context", "FLOAT"),
            ("score_vision", "FLOAT"),
            ("methodology_version", "VARCHAR(30)"),
            ("category_math_score", "FLOAT"),
            ("category_writing_score", "FLOAT"),
        ]
        for col_name, col_type in new_cols:
            if col_name not in lb_cols:
                cur.execute(f'ALTER TABLE leaderboard_entries ADD COLUMN {col_name} {col_type}')

        # tags column for model categorization
        if "tags" not in lb_cols:
            cur.execute("ALTER TABLE leaderboard_entries ADD COLUMN tags TEXT")

        # token_usage: add user_id and source columns
        tu_cols = {r[1] for r in cur.execute("PRAGMA table_info(token_usage)")}
        if "user_id" not in tu_cols:
            cur.execute("ALTER TABLE token_usage ADD COLUMN user_id INTEGER DEFAULT 1 REFERENCES users(id)")
        if "source" not in tu_cols:
            cur.execute("ALTER TABLE token_usage ADD COLUMN source VARCHAR(20) DEFAULT 'manual'")

        # email_accounts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                email_address VARCHAR(255) NOT NULL,
                provider_type VARCHAR(20) NOT NULL,
                access_token_encrypted TEXT,
                refresh_token_encrypted TEXT,
                token_expires_at DATETIME,
                imap_server VARCHAR(255),
                imap_username VARCHAR(255),
                imap_password_encrypted TEXT,
                sync_enabled BOOLEAN DEFAULT 1 NOT NULL,
                sync_interval_minutes INTEGER DEFAULT 60 NOT NULL,
                last_synced_at DATETIME,
                monitored_providers TEXT,
                created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_email_account_user ON email_accounts(user_id)")

        # synced_emails table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS synced_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_account_id INTEGER NOT NULL REFERENCES email_accounts(id),
                message_id VARCHAR(500) NOT NULL,
                provider VARCHAR(50) NOT NULL,
                email_date DATETIME NOT NULL,
                subject VARCHAR(500),
                parsed_data TEXT,
                token_usage_id INTEGER REFERENCES token_usage(id),
                synced_at DATETIME NOT NULL DEFAULT (datetime('now')),
                UNIQUE(email_account_id, message_id)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_se_email_account ON synced_emails(email_account_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_synced_email_date ON synced_emails(email_date)")

        # sync_logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_account_id INTEGER NOT NULL REFERENCES email_accounts(id),
                started_at DATETIME NOT NULL,
                finished_at DATETIME,
                status VARCHAR(20) DEFAULT 'running' NOT NULL,
                emails_fetched INTEGER DEFAULT 0,
                emails_parsed INTEGER DEFAULT 0,
                records_created INTEGER DEFAULT 0,
                error_message TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sl_email_account ON sync_logs(email_account_id)")

        conn.commit()
        conn.close()
    except Exception:
        pass  # Table may not exist yet — create_all handles that
