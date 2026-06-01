from __future__ import annotations
import base64
import email
import logging
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.email_auth import decrypt_token, refresh_access_token
from app.models import EmailAccount

logger = logging.getLogger("email_fetcher")

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _imap_date(dt: datetime) -> str:
    """Format a datetime as an IMAP-compatible date string (dd-Mon-yyyy) using English month abbreviations."""
    return f"{dt.day:02d}-{_MONTHS[dt.month - 1]}-{dt.year}"


AI_PROVIDER_SENDERS = [
    "openai.com",
    "anthropic.com",
    "google.com",
    "deepseek.com",
    "deepseek.ai",
    "xai.com",
    "mistral.ai",
    "cohere.com",
    "meta.ai",
    "perplexity.ai",
    # Chinese providers
    "zhipuai.cn",
    "zhipu.cn",
    "bigmodel.cn",
    "moonshot.cn",
    "moonshot.ai",
    "bytedance.com",
    "volcengine.com",
    "minimax.com",
    "minimaxi.com",
    "stepfun.com",
    "baichuan.cn",
    "baichuan.com",
    "01.ai",
    "lingyiwanwu.com",
    "alibaba-inc.com",
    "alibabacloud.com",
    "aliyun.com",
    "iflytek.com",
    "senseTime.com",
    "sensetime.com",
    "tencent.com",
    "baidu.com",
    # Korean / Asian
    "navercorp.com",
    "upstage.ai",
    # Others
    "stability.ai",
    "reka.ai",
    "ai21.com",
    "ibm.com",
    "databricks.com",
    "nvidia.com",
    "amazon.com",
    "aws.com",
]

# Broad sender patterns — subdomain matches (e.g., noreply@platform.deepseek.com)
# The list below is used for client-side FROM-address matching after IMAP fetch.
PROVIDER_SENDER_PATTERNS: dict[str, list[str]] = {
    "DeepSeek": [
        "deepseek.com", "deepseek.ai", "platform.deepseek.com",
        "mail.deepseek.com", "email.deepseek.com",
    ],
    "OpenAI": [
        "openai.com", "email.openai.com", "mail.openai.com",
        "noreply@openai.com", "notifications@openai.com",
    ],
    "Anthropic": [
        "anthropic.com", "email.anthropic.com", "mail.anthropic.com",
    ],
    "Google": [
        "google.com", "cloud.google.com", "googleapis.com",
    ],
    "xAI": ["xai.com", "mail.xai.com"],
    "Mistral AI": ["mistral.ai", "mail.mistral.ai"],
    "Mistral": ["mistral.ai", "mail.mistral.ai"],
    "Cohere": ["cohere.com", "mail.cohere.com"],
    "Meta": ["meta.ai", "mail.meta.ai"],
    "Perplexity": ["perplexity.ai", "mail.perplexity.ai"],
    # Chinese providers
    "Zhipu AI": ["zhipuai.cn", "zhipu.cn", "bigmodel.cn", "mail.bigmodel.cn"],
    "Zhipu": ["zhipuai.cn", "zhipu.cn", "bigmodel.cn"],
    "Moonshot AI": ["moonshot.cn", "moonshot.ai", "kimi.cn", "mail.kimi.cn"],
    "Moonshot": ["moonshot.cn", "moonshot.ai", "kimi.cn"],
    "ByteDance": ["bytedance.com", "volcengine.com", "mail.volcengine.com"],
    "MiniMax": ["minimax.com", "minimaxi.com", "mail.minimax.com"],
    "StepFun": ["stepfun.com", "mail.stepfun.com"],
    "Baichuan": ["baichuan.cn", "baichuan.com", "mail.baichuan.cn"],
    "01.AI": ["01.ai", "lingyiwanwu.com"],
    "Alibaba": ["alibaba-inc.com", "alibabacloud.com", "aliyun.com", "mail.aliyun.com"],
    "iFlytek": ["iflytek.com"],
    "SenseTime": ["sensetime.com", "sensetime.cn"],
    "Tencent": ["tencent.com"],
    "Baidu": ["baidu.com"],
    "Stability AI": ["stability.ai", "mail.stability.ai"],
    "Reka": ["reka.ai", "mail.reka.ai"],
    "AI21 Labs": ["ai21.com", "mail.ai21.com"],
    "IBM": ["ibm.com"],
    "Databricks": ["databricks.com"],
    "NVIDIA": ["nvidia.com"],
    "Amazon": ["amazon.com", "aws.com", "mail.amazon.com"],
}

PROVIDER_TO_DOMAINS: dict[str, list[str]] = {
    "OpenAI": ["openai.com", "email.openai.com", "mail.openai.com"],
    "Anthropic": ["anthropic.com", "email.anthropic.com", "mail.anthropic.com"],
    "Google": ["google.com", "cloud.google.com", "googleapis.com"],
    "DeepSeek": ["deepseek.com", "deepseek.ai", "platform.deepseek.com", "mail.deepseek.com"],
    "xAI": ["xai.com", "mail.xai.com"],
    "Mistral AI": ["mistral.ai", "mail.mistral.ai"],
    "Mistral": ["mistral.ai", "mail.mistral.ai"],
    "Cohere": ["cohere.com", "mail.cohere.com"],
    "Meta": ["meta.ai", "mail.meta.ai"],
    "Perplexity": ["perplexity.ai", "mail.perplexity.ai"],
    "Zhipu AI": ["zhipuai.cn", "zhipu.cn", "bigmodel.cn"],
    "Zhipu": ["zhipuai.cn", "zhipu.cn", "bigmodel.cn"],
    "Moonshot AI": ["moonshot.cn", "moonshot.ai", "kimi.cn"],
    "Moonshot": ["moonshot.cn", "moonshot.ai", "kimi.cn"],
    "ByteDance": ["bytedance.com", "volcengine.com"],
    "MiniMax": ["minimax.com", "minimaxi.com"],
    "StepFun": ["stepfun.com"],
    "Baichuan": ["baichuan.cn", "baichuan.com"],
    "01.AI": ["01.ai", "lingyiwanwu.com"],
    "Alibaba": ["alibaba-inc.com", "alibabacloud.com", "aliyun.com"],
    "iFlytek": ["iflytek.com"],
    "SenseTime": ["sensetime.com", "sensetime.cn"],
    "Tencent": ["tencent.com"],
    "Baidu": ["baidu.com"],
    "Stability AI": ["stability.ai"],
    "Reka": ["reka.ai"],
    "AI21 Labs": ["ai21.com"],
    "IBM": ["ibm.com"],
    "Databricks": ["databricks.com"],
    "NVIDIA": ["nvidia.com"],
    "Amazon": ["amazon.com", "aws.com"],
}


def _resolve_domains(monitored_providers: list[str] | None) -> list[str]:
    """Resolve provider names to email domains. Returns all domains if no filter."""
    if not monitored_providers:
        return list(AI_PROVIDER_SENDERS)
    domains: list[str] = []
    for name in monitored_providers:
        matched = PROVIDER_TO_DOMAINS.get(name)
        if matched:
            domains.extend(matched)
        else:
            # Try case-insensitive match
            for key, vals in PROVIDER_TO_DOMAINS.items():
                if key.lower() == name.lower():
                    domains.extend(vals)
                    break
    return list(set(domains)) if domains else list(AI_PROVIDER_SENDERS)


def build_search_queries(providers: list[str] | None = None, batch_size: int = 10) -> list[str]:
    """Build Gmail search queries, batching domains to avoid query length limits."""
    targets = providers if providers else AI_PROVIDER_SENDERS
    queries = []
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i + batch_size]
        parts = [f"from:{d}" for d in batch]
        if len(batch) == 1:
            queries.append(parts[0])
        else:
            queries.append("{" + " OR ".join(parts) + "}")
    return queries


def build_search_query(providers: list[str] | None = None) -> str:
    """Build a single Gmail search query. Use build_search_queries for large lists."""
    targets = providers if providers else AI_PROVIDER_SENDERS
    parts = [f"from:{d}" for d in targets]
    return "{" + " OR ".join(parts) + "}"


def parse_email_payload(payload: dict) -> tuple[str, str]:
    """Decode Gmail API message payload into (body_text, body_html)."""
    body_text = ""
    body_html = ""

    def _walk(part):
        nonlocal body_text, body_html
        mime_type = part.get("mimeType", "")
        data = part.get("body", {}).get("data", "")
        if mime_type == "text/plain" and data:
            body_text = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
        elif mime_type == "text/html" and data:
            body_html = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            _walk(sub)

    _walk(payload)
    return body_text, body_html


def decode_header_value(value: str) -> str:
    """Decode RFC 2047 encoded header values."""
    if not value:
        return ""
    try:
        decoded_parts = email.header.decode_header(value)
        return "".join(
            part.decode(charset or "utf-8", errors="replace") if isinstance(part, bytes) else part
            for part, charset in decoded_parts
        )
    except Exception:
        return value


async def fetch_messages(
    account: EmailAccount,
    since: datetime | None = None,
    max_results: int = 50,
    monitored_providers: list[str] | None = None,
) -> list[dict]:
    """Unified entry: dispatch to Gmail API or IMAP based on account.provider_type."""
    if account.provider_type == "gmail_oauth":
        return await _fetch_gmail_api(account, since, max_results, monitored_providers)
    elif account.provider_type == "imap":
        return await _fetch_imap(account, since, max_results, monitored_providers)
    else:
        raise ValueError(f"Unknown provider_type: {account.provider_type}")


async def _fetch_gmail_api(
    account: EmailAccount,
    since: datetime | None = None,
    max_results: int = 50,
    monitored_providers: list[str] | None = None,
) -> list[dict]:
    """Fetch recent emails via Gmail API. Uses batched queries to handle many domains."""
    if account.token_expires_at:
        now = datetime.now(timezone.utc)
        if account.token_expires_at < now:
            await refresh_access_token(account)

    access_token = decrypt_token(account.access_token_encrypted)
    headers = {"Authorization": f"Bearer {access_token}"}

    domains = _resolve_domains(monitored_providers)
    after_str = since.strftime("%Y/%m/%d") if since else None
    queries = build_search_queries(domains, batch_size=8)

    all_msg_ids: set[str] = set()

    async with httpx.AsyncClient() as client:
        for q in queries:
            query = q
            if after_str:
                query = f"{query} after:{after_str}"

            try:
                list_resp = await client.get(
                    f"{GMAIL_API_BASE}/messages",
                    headers=headers,
                    params={"q": query, "maxResults": max_results},
                )
                list_resp.raise_for_status()
                for m in list_resp.json().get("messages", []):
                    all_msg_ids.add(m["id"])
            except Exception as e:
                logger.warning("Gmail API search failed for query %s: %s", query[:80], e)

        if not all_msg_ids:
            return []

        results = []
        for msg_id in list(all_msg_ids)[:max_results]:
            get_resp = await client.get(
                f"{GMAIL_API_BASE}/messages/{msg_id}",
                headers=headers,
                params={"format": "full"},
            )
            get_resp.raise_for_status()
            full_msg = get_resp.json()

            headers_list = {h["name"].lower(): h["value"] for h in full_msg.get("payload", {}).get("headers", [])}
            subject = decode_header_value(headers_list.get("subject", ""))
            from_addr = decode_header_value(headers_list.get("from", ""))
            date_str = headers_list.get("date", "")
            try:
                msg_date = parsedate_to_datetime(date_str)
            except Exception:
                msg_date = datetime.now(timezone.utc)

            body_text, body_html = parse_email_payload(full_msg.get("payload", {}))

            results.append({
                "message_id": msg_id,
                "thread_id": full_msg.get("threadId", ""),
                "subject": subject,
                "from": from_addr,
                "date": msg_date,
                "body_text": body_text,
                "body_html": body_html,
            })

        return results


def _match_sender(from_addr: str, domains: list[str]) -> bool:
    """Check if from_addr matches any of the provider domains (substring match)."""
    addr_lower = from_addr.lower()
    return any(d in addr_lower for d in domains)


def _match_subject_keywords(subject: str) -> bool:
    """Check if subject contains token/usage/billing keywords related to AI usage."""
    # Use multi-word phrases to avoid false positives like "personal access token"
    keywords = [
        # English keywords
        "token usage", "token用量", "token使用量", "token消耗",
        "usage report", "usage summary", "usage", "用量报告", "使用报告",
        "api usage", "api用量",
        "monthly usage", "daily usage", "weekly usage", "用量统计", "用量",
        "billing", "账单", "账单报告", "invoice", "计费账单",
        "消费", "计费", "credit usage", "credit", "余额",
        "quota", "配额",
        "platform usage", "platform用量",
        # Common Chinese provider email subjects
        "使用情况", "使用明细", "消费明细", "消费记录", "消费账单",
        "token统计", "token使用", "token消耗", "token明细",
        "调用的token", "调用明细", "调用统计",
        "费用", "费用明细", "费用账单", "费用报告",
        "扣费", "扣费明细", "扣款",
        "用量提醒", "用量通知", "额度",
        "api调用", "apikey使用",
        "资源用量", "资源消耗", "资源使用",
        "模型调用", "模型使用",
        "本月用量", "本月消费", "本月账单",
        "周报", "月报", "日报",
        "platform", "后台用量", "后台消费",
        "report", "summary", "statement",
        "activity", "history",
    ]
    subj_lower = subject.lower()
    return any(kw.lower() in subj_lower for kw in keywords)


async def _fetch_imap(
    account: EmailAccount,
    since: datetime | None = None,
    max_results: int = 100,
    monitored_providers: list[str] | None = None,
) -> list[dict]:
    """Fetch recent emails via IMAP. Uses SINCE search + subject keyword search."""
    import imaplib
    import email as email_lib

    server = account.imap_server
    username = account.imap_username or account.email_address
    password = decrypt_token(account.imap_password_encrypted)
    domains = _resolve_domains(monitored_providers)

    conn = imaplib.IMAP4_SSL(server, 993, timeout=30)
    try:
        conn.login(username, password)
        status, _ = conn.select("INBOX")
        if status != "OK":
            return []

        all_uids: set[bytes] = set()

        # Strategy 1: Search by SINCE date (all recent emails)
        if since:
            search_criteria = f"SINCE {_imap_date(since)}"
        else:
            search_criteria = "ALL"

        status, msg_ids = conn.uid("SEARCH", None, search_criteria)
        if status == "OK" and msg_ids[0]:
            all_uids.update(msg_ids[0].split())

        # Strategy 2: Also search by subject keywords (may find emails missed by SINCE)
        subject_keywords = [
            "token", "usage", "billing", "invoice",
            "用量", "消费", "账单", "token", "费用",
        ]
        for kw in subject_keywords:
            status, msg_ids = conn.uid("SEARCH", None, f'SUBJECT "{kw}"')
            if status == "OK" and msg_ids[0]:
                all_uids.update(msg_ids[0].split())

        if not all_uids:
            return []

        # Process newest first (sorted by UID, take up to max_results * 3 for broader coverage)
        uids = sorted(all_uids, key=lambda x: int(x), reverse=True)[:max_results * 3]

        results = []
        for uid in uids:
            if len(results) >= max_results:
                break

            status, data = conn.uid("FETCH", uid, "(BODY.PEEK[] INTERNALDATE)")
            if status != "OK":
                continue
            if not data or not isinstance(data[0], tuple):
                continue
            raw_email = data[0][1]
            parsed = email_lib.message_from_bytes(raw_email)

            from_addr = str(parsed.get("From", ""))
            subject_raw = ""
            subject_header = parsed.get("Subject")
            if subject_header:
                decoded = email.header.decode_header(subject_header)
                if decoded:
                    first = decoded[0]
                    subject_raw = str(first[0] if isinstance(first[0], bytes) and first[1] else first[0])
                    if isinstance(subject_raw, bytes):
                        try:
                            subject_raw = subject_raw.decode(first[1] or "utf-8", errors="replace")
                        except Exception:
                            subject_raw = subject_raw.decode("utf-8", errors="replace")

            # Filter: pass if sender domain matches OR subject matches keywords
            matches_sender = _match_sender(from_addr, domains)
            matches_subject = _match_subject_keywords(subject_raw) if subject_raw else False

            if not matches_sender and not matches_subject:
                continue

            body_text = ""
            body_html = ""
            if parsed.is_multipart():
                for part in parsed.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain" and not body_text:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body_text = payload.decode("utf-8", errors="replace")
                    elif ctype == "text/html" and not body_html:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body_html = payload.decode("utf-8", errors="replace")
            else:
                payload = parsed.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body_text = payload.decode("utf-8", errors="replace")

            msg_date = parsedate_to_datetime(parsed.get("Date", "")) or datetime.now(timezone.utc)

            results.append({
                "message_id": str(uid, "utf-8"),
                "thread_id": "",
                "subject": subject_raw,
                "from": from_addr,
                "date": msg_date,
                "body_text": body_text,
                "body_html": body_html,
            })

        return results
    finally:
        try:
            conn.logout()
        except Exception:
            pass
