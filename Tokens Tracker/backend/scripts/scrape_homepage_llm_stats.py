"""
Scrape LLM STATS scores from llm-stats.com homepage table.
The homepage is server-rendered HTML, so we can parse it with stdlib tools.

Usage: (cd backend && python scripts/scrape_homepage_llm_stats.py)
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

HOMEPAGE_URL = "https://llm-stats.com"
KNOWN_PROVIDERS = [
    "Anthropic", "OpenAI", "Google", "Meta", "DeepSeek", "xAI",
    "Moonshot AI", "Zhipu AI", "ByteDance", "Alibaba Cloud / Qwen Team",
    "Alibaba", "MiniMax", "StepFun", "Nous Research", "Cohere",
    "AI21 Labs", "NVIDIA", "Amazon", "Perplexity", "IBM", "Databricks",
    "Mistral", "Stability AI", "Reka", "MiMo", "Muse", "LongCat",
    "OpenBMB", "Baidu", "Tencent", "iFlytek", "SenseTime", "Kling",
    "Hunyuan", "HiDream", "LG", "TII", "Upstage", "Adept", "Snowflake",
    "EleutherAI", "Allen AI",
]
KNOWN_PROVIDERS.sort(key=len, reverse=True)


class HomepageTableParser(HTMLParser):
    """Extract <tbody> <tr> <td> rows from the llm-stats.com homepage."""

    def __init__(self):
        super().__init__()
        self.in_tbody = 0
        self.in_tr = False
        self.in_cell = 0
        self.current_cell = ""
        self.current_row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.in_tbody += 1
        elif self.in_tbody and tag == "tr":
            self.in_tr = True
            self.current_row = []
        elif self.in_tr and tag in ("td", "th"):
            self.in_cell += 1
            self.current_cell = ""

    def handle_endtag(self, tag):
        if self.in_cell and tag in ("td", "th"):
            self.in_cell -= 1
            if self.in_cell == 0:
                self.current_row.append(self.current_cell.strip())
        elif self.in_tr and tag == "tr":
            self.in_tr = False
            if self.current_row:
                self.rows.append(self.current_row)
        elif self.in_tbody and tag == "tbody":
            self.in_tbody -= 1

    def handle_data(self, data):
        if self.in_cell > 0:
            self.current_cell += data


def fetch_page(page: int = 1) -> str:
    url = HOMEPAGE_URL
    if page > 1:
        url += f"?page={page}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TokenTracker/1.0", "Accept": "text/html"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode()


def strip_badges(text: str) -> str:
    """Remove UNRELEASED, NEW, UPDATED badges from model cell text."""
    return re.sub(r'(UNRELEASED|NEW\d*|UPDATED\d*)', '', text).strip()


def split_model_provider(name_cell: str) -> tuple[str, str]:
    """Split concatenated 'ModelNameProviderName' into (model_name, provider)."""
    cleaned = strip_badges(name_cell)
    # Remove extra whitespace between concatenated words
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    for prov in KNOWN_PROVIDERS:
        if cleaned.endswith(prov):
            model_name = cleaned[: -len(prov)].strip()
            return model_name, prov

    # Fallback: try regex for Uppercase-starting suffix
    m = re.match(r'^(.+?)\s+([A-Z][A-Za-z /&]+(?:\s+Team)?)$', cleaned)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    return cleaned, ""


def parse_models(html: str) -> list[dict]:
    parser = HomepageTableParser()
    parser.feed(html)

    models = []
    for row in parser.rows:
        if len(row) < 3:
            continue
        rank_str = row[0].strip().rstrip('.')
        if not rank_str.isdigit():
            continue

        rank = int(rank_str)
        name_cell = row[1]
        llm_stats_str = row[2]

        try:
            llm_stats = float(llm_stats_str) if llm_stats_str and llm_stats_str != "—" else None
        except ValueError:
            llm_stats = None

        model_name, provider = split_model_provider(name_cell)

        models.append({
            "rank": rank,
            "model_name": model_name,
            "provider": provider,
            "overall_score": llm_stats,
        })

    return models


def scrape_all(pages: int = 15) -> list[dict]:
    """Scrape all pages of the homepage leaderboard."""
    all_models = []
    for page in range(1, pages + 1):
        try:
            html = fetch_page(page)
            models = parse_models(html)
            if not models:
                break
            all_models.extend(models)
            print(f"  Page {page}: {len(models)} models (total: {len(all_models)})")
        except Exception as e:
            print(f"  Page {page}: error — {e}")
            break
    return all_models


def update_seed_models(models: list[dict], seed_path: str) -> int:
    """Update seed_models.json with scraped LLM STATS scores. Returns count updated."""
    with open(seed_path, "r", encoding="utf-8") as f:
        seed = json.load(f)

    updated = 0
    for m in models:
        if m["overall_score"] is None:
            continue
        # Match by model name (case-insensitive) or provider+name combo
        for sm in seed:
            sm_name = (sm.get("name") or "").lower()
            sm_prov = (sm.get("provider", {}).get("name") or sm.get("provider", {}).get("id") or "").lower()
            scraped_name = m["model_name"].lower()
            scraped_prov = m["provider"].lower()

            # Exact name match
            if sm_name == scraped_name:
                sm["overall_score"] = m["overall_score"]
                updated += 1
                break
            # Name contains or vice versa
            if sm_name and scraped_name and (sm_name in scraped_name or scraped_name in sm_name):
                if not scraped_prov or sm_prov == scraped_prov:
                    sm["overall_score"] = m["overall_score"]
                    updated += 1
                    break

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)

    return updated


if __name__ == "__main__":
    seed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

    print("Scraping llm-stats.com homepage for LLM STATS scores...")
    models = scrape_all(pages=15)
    print(f"\nTotal scraped: {len(models)} models")

    # Update seed files
    for seed_file in [
        "seed_models.json",
        "seed_image_models.json",
        "seed_video_models.json",
        "seed_tts_models.json",
        "seed_stt_models.json",
    ]:
        path = os.path.join(seed_dir, seed_file)
        if os.path.exists(path):
            n = update_seed_models(models, path)
            print(f"Updated {n} models in {seed_file}")

    # Print top 10 for verification
    print("\nTop 10 by LLM STATS:")
    for m in sorted(models, key=lambda x: x["overall_score"] or 0, reverse=True)[:10]:
        print(f"  #{m['rank']} {m['model_name']} ({m['provider']}): {m['overall_score']}")
