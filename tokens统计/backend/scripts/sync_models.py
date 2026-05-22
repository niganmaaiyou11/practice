"""
Sync vendor/model registry from OpenRouter and LiteLLM community data.

Usage: (cd backend && python scripts/sync_models.py)
"""
from __future__ import annotations
import json
import hashlib
import os
import sys
import urllib.request
from datetime import datetime, timezone

MODELS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "models.json"
)

# Whitelist: only these provider IDs are included in output.
# Maps raw IDs from OpenRouter/LiteLLM → canonical id, display name, color.
PROVIDER_WHITELIST: dict[str, tuple[str, str, str]] = {
    # Major Western
    "openai":          ("openai",     "OpenAI",              "#10a37f"),
    "anthropic":       ("anthropic",  "Anthropic",           "#d97757"),
    "google":          ("google",     "Google",              "#4285f4"),
    "gemini":          ("google",     "Google",              "#4285f4"),
    "meta-llama":      ("meta",       "Meta",                "#0668e1"),
    "meta":            ("meta",       "Meta",                "#0668e1"),
    "mistralai":       ("mistral",    "Mistral",             "#f90"),
    "mistral":         ("mistral",    "Mistral",             "#f90"),
    "cohere":          ("cohere",     "Cohere",              "#6936f5"),
    "x-ai":            ("xai",        "xAI",                 "#1da1f2"),
    "xai":             ("xai",        "xAI",                 "#1da1f2"),
    "perplexity":      ("perplexity", "Perplexity",          "#1abc9c"),
    "ai21":            ("ai21",       "AI21 Labs",           "#14b8a6"),
    "reka":            ("reka",       "Reka",                "#6366f1"),
    "amazon":          ("amazon",     "Amazon",              "#ff9900"),
    "stability":       ("stability",  "Stability AI",        "#4834d4"),
    "nvidia":          ("nvidia",     "NVIDIA",              "#76b900"),

    # Chinese / Asian
    "deepseek":        ("deepseek",   "DeepSeek",            "#4d6bfe"),
    "alibaba":         ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "qwen":            ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "dashscope":       ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "zhipuai":         ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "zhipu":           ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "zai":             ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "moonshotai":      ("moonshot",   "Moonshot (Kimi)",     "#8b5cf6"),
    "moonshot":        ("moonshot",   "Moonshot (Kimi)",     "#8b5cf6"),
    "01-ai":           ("01ai",       "01.AI (Yi)",          "#ec4899"),
    "01ai":            ("01ai",       "01.AI (Yi)",          "#ec4899"),
    "bytedance":       ("bytedance",  "ByteDance (Doubao)",  "#3252a8"),
    "minimax":         ("minimax",    "MiniMax",             "#f59e0b"),
    "baichuan":        ("baichuan",   "Baichuan",            "#0891b2"),
    "stepfun":         ("stepfun",    "StepFun",             "#9333ea"),

    # Enterprise / Other
    "ibm":             ("ibm",        "IBM",                 "#052fad"),
    "watsonx":         ("ibm",        "IBM",                 "#052fad"),
    "databricks":      ("databricks", "Databricks",          "#ff3621"),
}

# Pattern-based filtering: keep only models matching these prefixes
# This filters out fine-tuned variants, quantized versions, etc.
MODEL_PREFIX_ALLOWLIST = [
    # OpenAI — gpt-4o, gpt-4.1, gpt-5, gpt-5.3, gpt-5.4, gpt-5.5, o1, o3, o4, etc.
    "gpt-", "o1", "o1-", "o3", "o3-", "o4", "o4-", "computer-use",
    # Anthropic
    "claude-",
    # Google — gemini-2.5, gemini-3, gemini-3.1, gemma
    "gemini-", "gemma-", "palm",
    # Meta
    "llama-",
    # Mistral
    "mistral-", "codestral", "pixtral", "ministral",
    # Cohere
    "command-", "c4ai-",
    # DeepSeek
    "deepseek-",
    # xAI
    "grok-",
    # Perplexity
    "sonar", "pplx-",
    # Qwen
    "qwen", "qvq",
    # GLM / Zhipu
    "glm-", "cogview", "cogvideo",
    # Kimi
    "moonshot-", "kimi",
    # Yi
    "yi-",
    # Doubao
    "doubao-", "skylark-",
    # MiniMax
    "abab", "minimax-",
    # Baichuan
    "baichuan",
    # StepFun
    "step-",
    # AI21
    "jamba-", "jurassic-",
    # Reka
    "reka-",
    # Amazon
    "nova-", "titan-",
    # Stability
    "stable-",
    # NVIDIA
    "nemotron-",
    # IBM
    "granite-",
    # Databricks
    "dbrx-",
    # Perplexity (only native models, not re-hosts)
    "sonar", "pplx-",
]

# Models to always exclude (deprecated, test, internal, speed variants)
MODEL_EXCLUDE_PATTERNS = [
    "-dev", "-test", "-internal", "-eval", "-alpha", "-beta.",
    "ft-", "finetuned", "checkpoint", "deprecated", "-legacy", "-old",
    "-eval-", "-quant", "gguf", "gptq", "awq",
    "self-moderated", "papaya", "panda",
    # Speed/dated variants — keep only the canonical model name
    "-fast", "-non-reasoning", "-reasoning",
    # Not actual OpenAI models
    "gpt-oss",
]


def _color(pid: str) -> str:
    h = hashlib.md5(pid.encode()).hexdigest()
    return f"#{h[0:6]}"


def _allow_model(name: str) -> bool:
    """Check if a model name passes the prefix allowlist and exclusion filter."""
    lower = name.lower()
    for pat in MODEL_EXCLUDE_PATTERNS:
        if pat in lower:
            return False
    for prefix in MODEL_PREFIX_ALLOWLIST:
        if lower.startswith(prefix):
            return True
    return False


def load_existing():
    if not os.path.exists(MODELS_PATH):
        return {}
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_openrouter():
    """Fetch models from OpenRouter public API."""
    providers: dict[str, dict] = {}
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={"User-Agent": "TokenTracker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        for m in data.get("data", []):
            raw_id = m.get("id", "")
            if "/" not in raw_id:
                continue
            raw_pid, model_name = raw_id.split("/", 1)
            if raw_pid not in PROVIDER_WHITELIST:
                continue
            if not _allow_model(model_name):
                continue
            canonical_id, display_name, color = PROVIDER_WHITELIST[raw_pid]
            pid = canonical_id
            if pid not in providers:
                providers[pid] = {
                    "id": pid, "name": display_name, "color": color, "models": set()
                }
            providers[pid]["models"].add(model_name)
        total = sum(len(p["models"]) for p in providers.values())
        print(f"  OpenRouter: {len(providers)} providers, {total} models")
    except Exception as e:
        print(f"  OpenRouter fetch failed: {e}")
    return providers


def fetch_litellm():
    """Fetch models from LiteLLM community JSON as enrichment."""
    providers: dict[str, dict] = {}
    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
            headers={"User-Agent": "TokenTracker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        for key in data:
            if "/" not in key:
                continue
            raw_pid, model_name = key.split("/", 1)
            if raw_pid not in PROVIDER_WHITELIST:
                continue
            if not _allow_model(model_name):
                continue
            canonical_id, display_name, color = PROVIDER_WHITELIST[raw_pid]
            pid = canonical_id
            if pid not in providers:
                providers[pid] = {
                    "id": pid, "name": display_name, "color": color, "models": set()
                }
            providers[pid]["models"].add(model_name)
        total = sum(len(p["models"]) for p in providers.values())
        print(f"  LiteLLM: {len(providers)} providers, {total} models")
    except Exception as e:
        print(f"  LiteLLM fetch failed: {e}")
    return providers


def _parse_version(name: str) -> tuple:
    """Extract a sortable version tuple from a model name. Higher = newer.

    Date-based versions (e.g. qwen-plus-2025-07-28 where 2025 is a year) are
    demoted so semantic versions (e.g. qwen3.6-plus -> 3.6) sort above them.
    Padded to length 4 so (3,6) correctly sorts above (3,) after negation.
    """
    import re
    low = name.lower()
    nums = re.findall(r'(\d+)', low)
    ver = tuple(int(n) for n in nums) if nums else (0,)
    if ver and ver[0] >= 2020:
        ver = (0,) + ver
    while len(ver) < 4:
        ver = ver + (0,)
    return ver[:4]


def clamp_models(models: list[str], max_per_provider: int = 30) -> list[str]:
    """Keep the newest/most important models per provider, limit to max_per_provider."""
    if len(models) <= max_per_provider:
        return sorted(models)
    # Sort by version number descending (newest first), then alphabetically
    # We negate the version tuple for descending sort
    def sort_key(m: str) -> tuple:
        ver = _parse_version(m)
        # Negate for descending: larger version first
        neg_ver = tuple(-v for v in ver)
        # Prefer shorter names (less dated variants)
        return (neg_ver, len(m), m.lower())
    return sorted(models, key=sort_key)[:max_per_provider]


def main():
    print("Syncing model registry from OpenRouter + LiteLLM...")

    existing = load_existing()
    existing_map: dict[str, dict] = {}
    for p in existing.get("providers", []):
        existing_map[p["id"]] = p

    or_providers = fetch_openrouter()
    llm_providers = fetch_litellm()

    # Merge
    merged: dict[str, dict] = {}
    for pid, pdata in or_providers.items():
        merged[pid] = pdata
    for pid, pdata in llm_providers.items():
        if pid in merged:
            merged[pid]["models"] |= pdata["models"]
        else:
            merged[pid] = pdata

    # Build result, clamping model counts
    result_providers = []
    for pid, pdata in merged.items():
        models = clamp_models(sorted(pdata["models"]))
        if not models:
            continue
        # Preserve existing display name / color if present
        if pid in existing_map:
            pdata["name"] = existing_map[pid].get("name", pdata["name"])
            pdata["color"] = existing_map[pid].get("color", pdata["color"])
        result_providers.append({
            "id": pdata["id"],
            "name": pdata["name"],
            "color": pdata["color"],
            "models": models,
        })

    result_providers.sort(key=lambda p: p["name"].lower())

    result = {
        "providers": result_providers,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "openrouter+lite-llm",
    }

    os.makedirs(os.path.dirname(MODELS_PATH), exist_ok=True)
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    total_models = sum(len(p["models"]) for p in result_providers)
    print(f"Done: {len(result_providers)} providers, {total_models} models → {MODELS_PATH}")


if __name__ == "__main__":
    main()
