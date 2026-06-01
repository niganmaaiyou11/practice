from __future__ import annotations
import os
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timezone
from cryptography.fernet import Fernet

import httpx
from app.models import EmailAccount

# ── Load .env ─────────────────────────────────────
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = os.getenv("FERNET_KEY")
        if not key:
            key = Fernet.generate_key().decode()
            _set_env("FERNET_KEY", key)
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def _set_env(key: str, value: str):
    env_path = Path(__file__).resolve().parent.parent / ".env"
    with open(env_path, "a") as f:
        f.write(f"\n{key}={value}")


def encrypt_token(plain: str) -> str:
    return _get_fernet().encrypt(plain.encode()).decode()


def decrypt_token(cipher: str) -> str:
    return _get_fernet().decrypt(cipher.encode()).decode()


# ── Gmail OAuth ────────────────────────────────────

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def build_oauth_url(user_id: int) -> str:
    if not GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID not configured. Please use IMAP instead.")
    state_data = json.dumps({"user_id": user_id, "nonce": secrets.token_hex(16)})
    state_b64 = encrypt_token(state_data)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state_b64,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


def decode_state(state: str) -> dict:
    return json.loads(decrypt_token(state))


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code,
        })
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(account: EmailAccount) -> EmailAccount:
    refresh = decrypt_token(account.refresh_token_encrypted)
    async with httpx.AsyncClient() as client:
        resp = await client.post(GOOGLE_TOKEN_URL, data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh,
        })
        resp.raise_for_status()
        data = resp.json()
    account.access_token_encrypted = encrypt_token(data["access_token"])
    if "expires_in" in data:
        from datetime import timedelta
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
    return account


async def get_user_email(access_token: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/profile",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()["emailAddress"]


async def test_imap_connection(server: str, username: str, password: str) -> tuple[bool, str]:
    try:
        import imaplib
        conn = imaplib.IMAP4_SSL(server, 993, timeout=15)
        conn.login(username, password)
        conn.logout()
        return True, "Connection successful"
    except Exception as e:
        msg = str(e)
        if "AUTHENTICATIONFAILED" in msg.upper() or "LOGIN" in msg.upper():
            msg = "Authentication failed. Make sure you are using an authorization code (not your login password) for QQ/163/126 email."
        elif "Errno 11001" in msg or "getaddrinfo" in msg.lower():
            msg = f"Could not resolve server '{server}'. Check the IMAP server address."
        elif "timeout" in msg.lower() or "timed out" in msg.lower():
            msg = f"Connection timed out to {server}:993. Check your network or firewall settings."
        elif "SSL" in msg.upper() or "CERTIFICATE" in msg.upper():
            msg = f"SSL error connecting to {server}:993. The server may not support SSL on this port."
        return False, msg
