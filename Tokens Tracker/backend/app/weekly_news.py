from __future__ import annotations

import hashlib
import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import WeeklyNewsItem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    category: str


@dataclass
class FeedStatus:
    name: str
    url: str
    ok: bool = False
    items_count: int = 0
    error: str = ""
    fetched_at: datetime | None = None


# Global state for feed status tracking
_feed_statuses: list[FeedStatus] = []
_last_refresh_at: datetime | None = None
_last_refresh_count: int = 0


NEWS_SOURCES = [
    # Direct company blogs (verified working)
    NewsSource("OpenAI Blog", "https://openai.com/news/rss.xml", "industry"),
    NewsSource("Google AI Blog", "https://blog.google/technology/ai/rss/", "industry"),
    NewsSource("Hugging Face Blog", "https://huggingface.co/blog/feed.xml", "openSource"),
    NewsSource("GitHub Blog AI", "https://github.blog/tag/ai/feed/", "tool"),
    NewsSource("Microsoft AI Blog", "https://blogs.microsoft.com/ai/feed/", "industry"),
    NewsSource("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "industry"),
    NewsSource("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab", "industry"),
    # Google News aggregated feeds (reliable, for sources without direct RSS)
    NewsSource("Anthropic (Google News)", "https://news.google.com/rss/search?q=Anthropic+Claude&hl=en-US&gl=US&ceid=US:en", "model"),
    NewsSource("DeepSeek (Google News)", "https://news.google.com/rss/search?q=DeepSeek+AI&hl=zh-CN&gl=CN&ceid=CN:zh-Hans", "china"),
    NewsSource("Mistral (Google News)", "https://news.google.com/rss/search?q=Mistral+AI+model&hl=en-US&gl=US&ceid=US:en", "model"),
    NewsSource("AI Industry News", "https://news.google.com/rss/search?q=artificial+intelligence+LLM&hl=en-US&gl=US&ceid=US:en", "industry"),
    NewsSource("ArXiv CS.AI", "http://export.arxiv.org/rss/cs.AI", "openSource"),
]

CATEGORY_KEYWORDS = {
    "model": ["model", "gpt", "claude", "gemini", "llama", "qwen", "deepseek", "mistral", "benchmark",
              "llm", "language model", "reasoning", "inference", "fine-tun", "quantiz"],
    "openSource": ["open source", "open-source", "hugging face", "weights", "dataset",
                   "github.com", "apache", "mit license", "open-weight"],
    "tool": ["developer", "agent", "tool", "github", "eval", "observability", "coding",
             "ide", "plugin", "extension", "workflow", "pipeline"],
    "china": ["deepseek", "qwen", "alibaba", "zhipu", "moonshot", "baidu", "tencent", "china",
              "bytedance", "minimax", "stepfun", "baichuan", "iflytek", "sensetime"],
}

# Known AI entities for extraction
_MODEL_PATTERNS = [
    r"GPT-[\w.]+", r"Claude\s*[\d.]+(?:\s*Opus|\s*Sonnet|\s*Haiku)?",
    r"Gemini\s*[\w.]+", r"Llama\s*[\d.]+", r"Qwen\s*[\d\w]+",
    r"DeepSeek[\s-]*[\w]+", r"Mistral[\s-]*[\w]+", r"Grok[\s-]*[\w]+",
    r"Phi-[\d.]+", r"Command\s*R[\w]*", r"o[134][\s-]*(?:mini|preview)?",
    r"DALL[·-]?E\s*[\d]*", r"Stable\s*Diffusion\s*[\w.]+",
    r"Sora", r"Veo\s*[\d]*", r"Flux[\s.]*[\w]*",
    r"Whisper\s*[\w.]*", r"Midjourney\s*v?[\d.]*",
]
_COMPANY_PATTERNS = [
    r"OpenAI", r"Anthropic", r"Google", r"DeepSeek", r"Meta",
    r"Microsoft", r"Mistral", r"xAI", r"Apple", r"NVIDIA",
    r"Hugging\s*Face", r"Stability\s*AI", r"Cohere", r"Alibaba",
    r"Baidu", r"Tencent", r"ByteDance", r"Moonshot", r"Zhipu",
]
_PRICE_PATTERN = r"\$[\d.]+(?:/[\w]+)?(?:\s*(?:per|/)\s*(?:million|1M|1m)\s*tokens)?"
_VERSION_PATTERN = r"v[\d.]+(?:-[\w]+)?"


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _slugify(title: str, url: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:160]
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    return f"{base or 'ai-news'}-{digest}"


def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            return datetime.now(timezone.utc).replace(tzinfo=None)


def _child_text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
        for child in node:
            if child.tag.endswith(name) and child.text:
                return child.text.strip()
    return ""


def _entry_link(node: ET.Element) -> str:
    link = _child_text(node, ["link"])
    if link:
        return link
    for child in node:
        if child.tag.endswith("link"):
            href = child.attrib.get("href")
            if href:
                return href
    return ""


def _extract_key_entities(title: str, summary: str) -> dict:
    text = f"{title} {summary}"
    models = list(set(re.findall(r"(?:" + "|".join(_MODEL_PATTERNS) + ")", text, re.IGNORECASE)))
    companies = list(set(re.findall(r"(?:" + "|".join(_COMPANY_PATTERNS) + ")", text, re.IGNORECASE)))
    prices = list(set(re.findall(_PRICE_PATTERN, text, re.IGNORECASE)))
    versions = list(set(re.findall(_VERSION_PATTERN, text)))
    return {
        "models": models[:5],
        "companies": companies[:3],
        "prices": prices[:3],
        "versions": versions[:3],
    }


def _infer_category(source: NewsSource, title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return source.category


def _impact(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()
    if any(word in text for word in ["release", "launch", "new model", "benchmark", "agent", "pricing",
                                     "announce", "introduce", "billion", "gpt-5", "claude", "gemini"]):
        return "High"
    if any(word in text for word in ["update", "open source", "developer", "tool", "improve",
                                     "expand", "partner", "integrat"]):
        return "Medium"
    return "Watch"


def _reading_time(body: list[str]) -> str:
    words = sum(len(p.split()) for p in body)
    minutes = max(2, round(words / 180))
    return f"{minutes} min read"


def _build_body(title: str, summary: str, source_name: str, category: str, entities: dict) -> list[str]:
    lead = summary or f"{source_name} published an AI update worth tracking this week."

    # Build entity-aware context
    entity_line = ""
    if entities["models"]:
        entity_line = f"Key models mentioned: {', '.join(entities['models'][:3])}."
    elif entities["companies"]:
        entity_line = f"Key players: {', '.join(entities['companies'][:3])}."
    if entities["prices"]:
        entity_line += f" Pricing signals: {', '.join(entities['prices'][:2])}."

    context_map = {
        "model": "For model selection, the important question is how this changes quality, speed, context length, or total task cost in real workflows.",
        "industry": "For product teams, the update is a signal to watch platform direction, developer experience, and how quickly capabilities are moving into production tools.",
        "openSource": "For open-source adoption, the practical tradeoff remains model capability versus deployment control, infrastructure cost, and maintenance effort.",
        "tool": "For AI engineering teams, tooling updates matter most when they improve evaluation, observability, workflow reliability, or developer iteration speed.",
        "china": "For China-focused workloads, the key lens is price-performance, Chinese language quality, local ecosystem fit, and API availability.",
    }
    context = context_map.get(category, "For teams tracking AI adoption, this is worth comparing against existing models, tools, and usage patterns.")

    parts = [lead]
    if entity_line:
        parts.append(entity_line)
    parts.append(context)
    parts.append(f"Source: {source_name}. Automatically collected and published for the weekly AI briefing.")
    return parts


def _takeaways(title: str, category: str, impact: str, entities: dict) -> list[str]:
    labels = {
        "model": "Re-check model choices if this affects quality, speed, pricing, or context window.",
        "industry": "Watch whether this becomes a production feature rather than a demo capability.",
        "openSource": "Compare open deployment control against hosted API simplicity.",
        "tool": "Evaluate the update by workflow reliability, visibility, and total cost impact.",
        "china": "Test domestic models directly for Chinese-language and cost-sensitive scenarios.",
    }
    base = labels.get(category, "Track this update against your own AI usage needs.")

    takeaways = [base]
    if impact == "High":
        takeaways.append(f"High-priority signal — review and evaluate promptly: {title}")
    else:
        takeaways.append(f"Use this as a weekly signal, not a final decision: {title}")

    if entities["models"]:
        takeaways.append(f"Models to watch: {', '.join(entities['models'][:3])}")
    if entities["prices"]:
        takeaways.append(f"Pricing update: {', '.join(entities['prices'][:2])}")

    return takeaways


def _parse_feed(xml_text: str, source: NewsSource) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        # Try to fix encoding issues by replacing invalid chars
        cleaned = re.sub(r'[^\x09\x0A\x0D\x20-퟿-�]', '', xml_text)
        try:
            root = ET.fromstring(cleaned)
        except ET.ParseError:
            return []

    nodes = root.findall(".//item") or [n for n in root.iter() if n.tag.endswith("entry")]
    items = []
    for node in nodes[:10]:
        title = _strip_html(_child_text(node, ["title"]))
        if not title:
            continue
        summary = _strip_html(_child_text(node, ["description", "summary", "content", "encoded"]))
        url = _entry_link(node)
        if not url:
            continue

        # Google News: extract actual source name from <source> tag
        source_name = source.name
        source_tag = node.find("source")
        if source_tag is not None and source_tag.text:
            source_name = _strip_html(source_tag.text)

        published_raw = _child_text(node, ["pubDate", "published", "updated"])
        category = _infer_category(source, title, summary)
        impact = _impact(title, summary)
        entities = _extract_key_entities(title, summary)
        body = _build_body(title, summary, source_name, category, entities)
        items.append({
            "slug": _slugify(title, url),
            "title": title[:500],
            "summary": (summary or title)[:1000],
            "category": category,
            "impact": impact,
            "reading_time": _reading_time(body),
            "published_at": _parse_date(published_raw),
            "source_name": source_name,
            "source_url": url,
            "body_json": json.dumps(body, ensure_ascii=False),
            "takeaways_json": json.dumps(_takeaways(title, category, impact, entities), ensure_ascii=False),
            "fetched_at": datetime.now(timezone.utc).replace(tzinfo=None),
            "is_published": True,
        })
    return items


async def fetch_weekly_news() -> tuple[list[dict], list[FeedStatus]]:
    """Fetch news from all sources. Returns (items, feed_statuses)."""
    global _feed_statuses, _last_refresh_at, _last_refresh_count

    results: list[dict] = []
    statuses: list[FeedStatus] = []

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        for source in NEWS_SOURCES:
            status = FeedStatus(name=source.name, url=source.url)
            try:
                response = await client.get(source.url, headers={"User-Agent": "AI Token Tracker Weekly Bot"})
                response.raise_for_status()
                parsed = _parse_feed(response.text, source)
                results.extend(parsed)
                status.ok = True
                status.items_count = len(parsed)
                logger.info("Feed '%s' fetched successfully: %d items", source.name, len(parsed))
            except httpx.TimeoutException:
                status.error = "Request timed out (20s)"
                logger.warning("Feed '%s' timed out: %s", source.name, source.url)
            except httpx.HTTPStatusError as e:
                status.error = f"HTTP {e.response.status_code}"
                logger.warning("Feed '%s' HTTP error %s: %s", source.name, e.response.status_code, source.url)
            except Exception as e:
                status.error = str(e)[:200]
                logger.warning("Feed '%s' failed: %s — %s", source.name, source.url, e)
            status.fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)
            statuses.append(status)

    _feed_statuses = statuses
    _last_refresh_at = datetime.now(timezone.utc).replace(tzinfo=None)
    _last_refresh_count = len(results)

    ok_count = sum(1 for s in statuses if s.ok)
    logger.info("Weekly news fetch complete: %d/%d sources OK, %d items total",
                ok_count, len(statuses), len(results))
    return results, statuses


def publish_weekly_items(db: Session, items: list[dict]) -> int:
    created = 0
    for item in items:
        existing = db.query(WeeklyNewsItem).filter(WeeklyNewsItem.source_url == item["source_url"]).first()
        if existing:
            continue
        db.add(WeeklyNewsItem(**item))
        try:
            db.commit()
            created += 1
        except IntegrityError:
            db.rollback()
    return created


def weekly_item_to_dict(item: WeeklyNewsItem) -> dict:
    return {
        "slug": item.slug,
        "title": item.title,
        "summary": item.summary,
        "category": item.category,
        "impact": item.impact,
        "reading_time": item.reading_time,
        "published_at": item.published_at,
        "source_name": item.source_name,
        "source_url": item.source_url,
        "body": json.loads(item.body_json),
        "takeaways": json.loads(item.takeaways_json),
    }


def get_refresh_status() -> dict:
    """Return current refresh status for API consumption."""
    return {
        "last_refresh_at": _last_refresh_at,
        "last_refresh_count": _last_refresh_count,
        "sources": [
            {
                "name": s.name,
                "url": s.url,
                "ok": s.ok,
                "items_count": s.items_count,
                "error": s.error,
                "fetched_at": s.fetched_at,
            }
            for s in _feed_statuses
        ],
    }
