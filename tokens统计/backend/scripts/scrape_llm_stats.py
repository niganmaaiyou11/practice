"""
Scrape AI model leaderboard data from llm-stats.com.

The /stats/v1/ API endpoints were removed in 2026. This script now loads
data from seed_models.json (built from the category leaderboard pages at
llm-stats.com/leaderboards/best-ai-for-{coding,reasoning,writing}).

To refresh seed data, run: python scripts/build_merged_seed.py

Usage: (cd backend && python scripts/scrape_llm_stats.py)
"""
from __future__ import annotations
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

# Allow running from backend/ or backend/scripts/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.database import SessionLocal, run_migrations
from app.crud import upsert_leaderboard_entry


API_BASE = "https://llm-stats.com"
# The public API endpoint (discovered from the site's developer page)
API_MODELS_URL = f"{API_BASE}/stats/v1/models"
# Category rankings endpoints for composite category scores
RANKINGS_URL = f"{API_BASE}/stats/v1/rankings"


def fetch_models():
    """Fetch all models from llm-stats.com public API.

    The /stats/v1/models endpoint returns 404 as of 2026.
    We try it first, then fall back to seed data.
    """
    try:
        req = urllib.request.Request(
            API_MODELS_URL,
            headers={"User-Agent": "TokenTracker/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return None
    except Exception:
        return None


def fetch_models_fallback():
    """Fallback: scrape the leaderboard HTML page and extract embedded data."""
    req = urllib.request.Request(
        f"{API_BASE}/leaderboards/llm-leaderboard",
        headers={"User-Agent": "TokenTracker/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode()
        # Try to find embedded JSON data in __NEXT_DATA__ or similar patterns
        import re
        # Look for JSON-LD or script data
        patterns = [
            r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.DOTALL)
            if m:
                return json.loads(m.group(1))
        print("  No embedded data found in HTML fallback.")
        return None
    except Exception as e:
        print(f"  Fallback fetch failed: {e}")
        return None


def fetch_category_rankings(categories: list[str]) -> dict[str, dict[str, float | None]]:
    """Fetch TrueSkill rankings by category. Returns {model_slug: {category: score}}."""
    result: dict[str, dict[str, float | None]] = {}
    for cat in categories:
        url = f"{RANKINGS_URL}?category={cat}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TokenTracker/1.0", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            # Handle different response shapes
            rankings = data if isinstance(data, list) else data.get("rankings") or data.get("data") or []
            for r in rankings:
                slug = r.get("model_id") or r.get("model_slug") or r.get("id", "")
                score = r.get("score") or r.get("trueskill_score") or r.get("rating")
                if slug and score is not None:
                    result.setdefault(slug, {})[cat] = float(score)
        except Exception as e:
            print(f"  Category rankings fetch failed for '{cat}': {e}")
    return result


def map_model(raw: dict) -> dict | None:
    """Map a raw API model object to our DB column dict. Returns None if unusable."""
    slug = raw.get("id") or raw.get("slug") or raw.get("model_slug", "")
    name = raw.get("name") or raw.get("model_name") or raw.get("display_name", "")
    if not slug or not name:
        return None

    # Provider / organization — prefer the display name (Title case) so
    # rows stay consistent regardless of whether the source gives us a
    # provider "id" (lowercase) or just a "name" field.
    provider_raw = raw.get("provider") or {}
    if isinstance(provider_raw, dict):
        provider = (
            provider_raw.get("name")
            or provider_raw.get("displayName")
            or provider_raw.get("id")
            or provider_raw.get("slug", "")
        )
        organization = provider_raw.get("name") or provider_raw.get("displayName", "")
    else:
        provider = str(provider_raw)
        organization = provider

    if not provider:
        # Try organization field
        org_raw = raw.get("organization") or {}
        if isinstance(org_raw, dict):
            provider = (
                org_raw.get("name")
                or org_raw.get("displayName")
                or org_raw.get("id")
                or org_raw.get("slug", "")
            )
            organization = org_raw.get("name") or org_raw.get("displayName", "")
        else:
            provider = str(org_raw) if org_raw else ""
            organization = provider

    provider = _canonical_provider(provider)
    organization = organization or provider

    # Normalize slug: if it contains "provider/", strip the prefix so
    # seed entries and live API entries don't end up duplicated.
    canonical_slug = slug.split("/", 1)[1] if "/" in slug else slug

    # Scores
    scores = raw.get("scores") or raw.get("benchmarks") or {}
    if not isinstance(scores, dict):
        scores = {}

    def _f(key, *alts):
        for a in [key] + list(alts):
            v = scores.get(a)
            if v is not None:
                return float(v)
        return None

    # Pricing
    pricing = raw.get("pricing") or raw.get("price") or {}
    if not isinstance(pricing, dict):
        pricing = {}
    price_input = pricing.get("input") or pricing.get("input_price") or pricing.get("prompt")
    price_output = pricing.get("output") or pricing.get("output_price") or pricing.get("completion")
    if price_input is not None:
        price_input = float(price_input)
    if price_output is not None:
        price_output = float(price_output)

    # Benchmark sub-scores
    s_gpqa     = _f("gpqa_diamond", "gpqa", "GPQA Diamond")
    s_mmlu     = _f("mmlu", "MMLU")
    s_mmlupro  = _f("mmlu_pro", "mmlu-pro", "MMLU-Pro")
    s_math     = _f("math", "MATH")
    s_humanev  = _f("humaneval", "HumanEval", "human_eval")
    s_swe      = _f("swebench_verified", "swebench", "swe-bench", "SWE-Bench Verified")
    s_codearen = _f("coding_arena", "coding-arena", "Coding Arena")

    # Category scores from the new llm-stats.com leaderboard pages
    # Each category page provides its own score (0-100 scale)
    cat_scores_raw = raw.get("scores") or raw.get("category_scores") or {}
    s_coding = _f("coding", "Coding", "code") or _extract_axis(scores, raw, "coding")
    s_math = _f("math", "Math", "mathematics") or _extract_axis(scores, raw, "math")
    s_reasoning = _f("reasoning", "Reasoning") or _extract_axis(scores, raw, "reasoning")
    s_writing = _f("writing", "Writing") or _extract_axis(scores, raw, "writing")

    # Use the LLM STATS overall score directly from llm-stats.com
    overall = raw.get("overall_score")
    if overall is not None:
        overall = float(overall)

    # Rank — derived from composite at the end of main(); ignore any
    # rank value the upstream feed reports (often inconsistent with score).
    rank = None

    # Speed
    tps = raw.get("tokens_per_second") or raw.get("speed") or raw.get("throughput")
    if tps is not None:
        tps = float(tps)

    # Context
    ctx = raw.get("context_window") or raw.get("context") or raw.get("max_tokens")
    if ctx is not None:
        ctx = int(ctx)

    max_out = raw.get("max_output_tokens") or raw.get("max_output") or raw.get("output_tokens")
    if max_out is not None:
        max_out = int(max_out)

    # Modalities
    mods = raw.get("modalities") or raw.get("modality") or []
    if isinstance(mods, list):
        mods = ",".join(mods)
    elif not isinstance(mods, str):
        mods = None

    return {
        "model_slug": canonical_slug,
        "model_name": name,
        "provider": provider,
        "organization": organization or None,
        "overall_score": overall,
        "rank_overall": rank,
        "score_gpqa": s_gpqa,
        "score_mmlu": s_mmlu,
        "score_mmlu_pro": s_mmlupro,
        "score_math": s_math,
        "score_humaneval": s_humanev,
        "score_swebench": s_swe,
        "score_coding_arena": s_codearen,
        "score_reasoning": s_reasoning,
        "score_coding": s_coding,
        "score_knowledge": _extract_axis(scores, raw, "knowledge"),
        "score_tool_use": _extract_axis(scores, raw, "tool_use"),
        "score_long_context": _extract_axis(scores, raw, "long_context"),
        "score_vision": _extract_axis(scores, raw, "vision"),
        "category_math_score": s_math,
        "category_writing_score": s_writing,
        "methodology_version": "llm-stats",
        "tokens_per_second": tps,
        "price_input": price_input,
        "price_output": price_output,
        "context_window": ctx,
        "max_output_tokens": max_out,
        "knowledge_cutoff": raw.get("knowledge_cutoff") or raw.get("training_cutoff") or None,
        "modalities": mods,
        "tags": raw.get("tags"),
        "category": raw.get("category") or "llm",
        "arena_rating": raw.get("arena_rating"),
        "output_resolution": raw.get("output_resolution"),
        "latency": raw.get("latency"),
        "raw_data": json.dumps(raw, ensure_ascii=False),
        "fetched_at": datetime.now(timezone.utc),
    }


def _extract_axis(scores: dict, raw: dict, axis: str) -> float | None:
    """Extract a pre-computed axis score from the API response."""
    # Check scores dict first
    v = scores.get(axis) or scores.get(f"axis_{axis}")
    if v is not None:
        return round(float(v), 4) if float(v) <= 1 else round(float(v) / 100, 4)
    # Check raw top-level
    v = raw.get(axis) or raw.get(f"score_{axis}") or raw.get(f"axis_{axis}")
    if v is not None:
        return round(float(v), 4) if float(v) <= 1 else round(float(v) / 100, 4)
    return None


# Canonical provider names — keep display casing consistent across
# both the seed data and whatever llm-stats.com returns.
PROVIDER_NAMES = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "google": "Google",
    "meta": "Meta",
    "deepseek": "DeepSeek",
    "xai": "xAI",
    "moonshot": "Moonshot AI",
    "moonshot ai": "Moonshot AI",
    "kimi": "Moonshot AI",
    "zhipu": "Zhipu AI",
    "zhipu ai": "Zhipu AI",
    "glm": "Zhipu AI",
    "alibaba": "Alibaba",
    "qwen": "Alibaba",
    "alibaba (qwen)": "Alibaba",
    "mistral": "Mistral",
    "mistral ai": "Mistral",
    "mistralai": "Mistral",
    "cohere": "Cohere",
    "ai21": "AI21 Labs",
    "ai21 labs": "AI21 Labs",
    "nvidia": "NVIDIA",
    "amazon": "Amazon",
    "aws": "Amazon",
    "perplexity": "Perplexity",
    "stepfun": "StepFun",
    "minimax": "MiniMax",
    "bytedance": "ByteDance",
    "doubao": "ByteDance",
    "stability": "Stability AI",
    "stability ai": "Stability AI",
    "reka": "Reka",
    "ibm": "IBM",
    "databricks": "Databricks",
    "mimo": "MiMo",
    "muse": "Muse",
    "longcat": "LongCat",
    "openbmb": "OpenBMB",
    "nous research": "Nous Research",
    "nous": "Nous Research",
}


def _canonical_provider(raw: str) -> str:
    if not raw:
        return ""
    key = str(raw).strip().lower()
    return PROVIDER_NAMES.get(key, raw if raw[0].isupper() else raw.title())


def extract_models(data) -> list[dict]:
    """Extract model list from the API response, handling different shapes."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    # Common shapes
    for key in ("models", "data", "entries", "results", "items"):
        if key in data and isinstance(data[key], list):
            return data[key]
    # Maybe it's nested: { props: { pageProps: { models: [...] } } }
    for k in ("props", "pageProps", "initialState", "state"):
        if k in data and isinstance(data[k], dict):
            nested = extract_models(data[k])
            if nested:
                return nested
    return []


def _ensure_tables():
    """Create tables if they don't exist (idempotent)."""
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)


def main():
    _ensure_tables()
    run_migrations()

    data = fetch_models()
    models_raw = extract_models(data)
    if not models_raw:
        models_raw = SEED_MODELS

    # Map all models — overall_score comes directly from llm-stats.com LLM STATS
    mapped_models: list[dict] = []
    for m in models_raw:
        mapped = map_model(m)
        if mapped is None:
            continue
        mapped_models.append(mapped)

    # Upsert all (overall_score already set from upstream LLM STATS)
    db = SessionLocal()
    upserted = 0
    try:
        for mapped in mapped_models:
            upsert_leaderboard_entry(db, mapped)
            upserted += 1
        _assign_ranks(db)
        print(f"Done: {upserted} models upserted, ranks reassigned.")
    finally:
        db.close()
    return upserted


def _assign_ranks(db) -> None:
    """Set rank_overall on every row to its position in the score-sorted list."""
    from app.models import LeaderboardEntry
    from sqlalchemy import desc
    rows = (
        db.query(LeaderboardEntry)
        .order_by(desc(LeaderboardEntry.overall_score).nullslast())
        .all()
    )
    for i, r in enumerate(rows, start=1):
        r.rank_overall = i if r.overall_score is not None else None
    db.commit()


# ── Built-in seed data (used when llm-stats.com is unreachable) ──

def _load_seed_models():
    """Load seed models from all 5 JSON files (generated from llm-stats.com category pages)."""
    import os as _os
    seed_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "data")
    all_models = []
    categories = {
        "seed_models.json": "llm",
        "seed_image_models.json": "image",
        "seed_video_models.json": "video",
        "seed_tts_models.json": "tts",
        "seed_stt_models.json": "stt",
    }
    for filename, category in categories.items():
        seed_path = _os.path.join(seed_dir, filename)
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                models = json.load(f)
            for m in models:
                m.setdefault("category", category)
            all_models.extend(models)
        except Exception:
            pass
    if all_models:
        return all_models
    # Fallback: return inline minimal list
    return [
        {"id":"claude-mythos-preview","name":"Claude Mythos Preview","provider":{"id":"anthropic","name":"Anthropic"},"scores":{"coding":57.3,"math":61.7,"reasoning":71.3},"overall_score":63.4,"tokens_per_second":50,"pricing":{},"context_window":200000,"max_output_tokens":16384,"knowledge_cutoff":"2025-12","modalities":["text"],"category":"llm"},
        {"id":"deepseek-v4-pro-max","name":"DeepSeek-V4-Pro-Max","provider":{"id":"deepseek","name":"DeepSeek"},"scores":{"coding":45.0,"math":53.8,"reasoning":57.7},"overall_score":52.2,"tokens_per_second":76,"pricing":{"input":2.09},"context_window":1000000,"max_output_tokens":32768,"knowledge_cutoff":"2025-12","modalities":["text"],"category":"llm"},
        {"id":"gpt-5.5","name":"GPT-5.5","provider":{"id":"openai","name":"OpenAI"},"scores":{"coding":53.1,"math":48.6,"reasoning":63.1,"writing":30.8},"overall_score":48.9,"tokens_per_second":31,"pricing":{"input":10},"context_window":1100000,"max_output_tokens":16384,"knowledge_cutoff":"2025-12","modalities":["text"],"category":"llm"},
    ]

SEED_MODELS = _load_seed_models()

# Old v1.0 seed data (pre-June 2025) removed — models now come from seed_models.json.
# If you need the old data for reference, check git history.

if __name__ == "__main__":
    main()
