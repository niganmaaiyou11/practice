"""
Sync vendor/model registry from OpenRouter, LiteLLM community data, and local supplemental entries.

Usage: (cd backend && python scripts/sync_models.py)
"""
from __future__ import annotations
import hashlib
import html
import http.client
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

MODELS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "models.json"
)

PROVIDER_WHITELIST: dict[str, tuple[str, str, str]] = {
    # Major Western
    "openai":          ("openai",     "OpenAI",              "#10a37f"),
    "anthropic":       ("anthropic",  "Anthropic",           "#d97757"),
    "claude":          ("anthropic",  "Anthropic",           "#d97757"),
    "google":          ("google",     "Google",              "#4285f4"),
    "gemini":          ("google",     "Google",              "#4285f4"),
    "google-ai-studio": ("google",    "Google",              "#4285f4"),
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
    "bedrock":         ("amazon",     "Amazon",              "#ff9900"),
    "stability":       ("stability",  "Stability AI",        "#4834d4"),
    "nvidia":          ("nvidia",     "NVIDIA",              "#76b900"),
    "together_ai":     ("together",   "Together AI",         "#111827"),
    "together":        ("together",   "Together AI",         "#111827"),
    "fireworks_ai":    ("fireworks",  "Fireworks AI",        "#f97316"),
    "fireworks":       ("fireworks",  "Fireworks AI",        "#f97316"),
    "groq":            ("groq",       "Groq",                "#f55036"),
    "cerebras":        ("cerebras",   "Cerebras",            "#f97316"),

    # Chinese / Asian
    "deepseek":        ("deepseek",   "DeepSeek",            "#4d6bfe"),
    "alibaba":         ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "qwen":            ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "dashscope":       ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "aliyun":          ("alibaba",    "Alibaba (Qwen)",      "#ff6a00"),
    "zhipuai":         ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "zhipu":           ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "zai":             ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "bigmodel":        ("zhipu",      "Zhipu (GLM)",         "#3859ff"),
    "moonshotai":      ("moonshot",   "Moonshot (Kimi)",     "#8b5cf6"),
    "moonshot":        ("moonshot",   "Moonshot (Kimi)",     "#8b5cf6"),
    "kimi":            ("moonshot",   "Moonshot (Kimi)",     "#8b5cf6"),
    "01-ai":           ("01ai",       "01.AI (Yi)",          "#ec4899"),
    "01ai":            ("01ai",       "01.AI (Yi)",          "#ec4899"),
    "yi":              ("01ai",       "01.AI (Yi)",          "#ec4899"),
    "bytedance":       ("bytedance",  "ByteDance (Doubao)",  "#3252a8"),
    "volcengine":      ("bytedance",  "ByteDance (Doubao)",  "#3252a8"),
    "doubao":          ("bytedance",  "ByteDance (Doubao)",  "#3252a8"),
    "minimax":         ("minimax",    "MiniMax",             "#f59e0b"),
    "baichuan":        ("baichuan",   "Baichuan",            "#0891b2"),
    "stepfun":         ("stepfun",    "StepFun",             "#9333ea"),
    "step":            ("stepfun",    "StepFun",             "#9333ea"),
    "xiaomi":          ("xiaomi",     "Xiaomi",              "#ff6900"),
    "mimo":            ("xiaomi",     "Xiaomi",              "#ff6900"),
    "tencent":         ("tencent",    "Tencent (Hunyuan)",   "#0052d9"),
    "hunyuan":         ("tencent",    "Tencent (Hunyuan)",   "#0052d9"),
    "baidu":           ("baidu",      "Baidu (ERNIE)",       "#2932e1"),
    "ernie":           ("baidu",      "Baidu (ERNIE)",       "#2932e1"),
    "iflytek":         ("iflytek",    "iFlytek (Spark)",     "#e1251b"),
    "spark":           ("iflytek",    "iFlytek (Spark)",     "#e1251b"),
    "huawei":          ("huawei",     "Huawei (Pangu)",      "#cf0a2c"),
    "pangu":           ("huawei",     "Huawei (Pangu)",      "#cf0a2c"),
    "sensetime":       ("sensetime",  "SenseTime",           "#7c3aed"),
    "sensenova":       ("sensetime",  "SenseTime",           "#7c3aed"),
    "siliconflow":     ("siliconflow", "SiliconFlow",        "#111827"),

    # Enterprise / Other
    "ibm":             ("ibm",        "IBM",                 "#052fad"),
    "watsonx":         ("ibm",        "IBM",                 "#052fad"),
    "databricks":      ("databricks", "Databricks",          "#ff3621"),
}

MODEL_PREFIX_ALLOWLIST = [
    "gpt-", "o1", "o1-", "o3", "o3-", "o4", "o4-", "computer-use",
    "claude-",
    "gemini-", "gemma-", "palm",
    "llama-",
    "mistral-", "codestral", "pixtral", "ministral",
    "command-", "c4ai-",
    "deepseek-",
    "grok-",
    "sonar", "pplx-",
    "qwen", "qvq",
    "glm-", "cogview", "cogvideo",
    "moonshot-", "kimi",
    "yi-",
    "doubao-", "skylark-",
    "abab", "minimax-",
    "baichuan",
    "step-",
    "jamba-", "jurassic-",
    "reka-",
    "nova-", "titan-",
    "stable-",
    "nemotron-",
    "granite-",
    "dbrx-",
    "hunyuan", "ernie", "spark", "pangu", "mimo", "sense", "sensenova",
]

MODEL_EXCLUDE_PATTERNS = [
    "-dev", "-test", "-internal", "-eval", "-alpha", "-beta.",
    "ft-", "finetuned", "checkpoint", "deprecated", "-legacy", "-old",
    "-eval-", "-quant", "gguf", "gptq", "awq",
    "self-moderated", "papaya", "panda",
    "-fast", "-non-reasoning", "-reasoning",
]

ARTIFICIAL_ANALYSIS_PREFIXES = {
    "gpt": "openai",
    "o1": "openai",
    "o3": "openai",
    "o4": "openai",
    "claude": "anthropic",
    "gemini": "google",
    "gemma": "google",
    "deepseek": "deepseek",
    "grok": "xai",
    "qwen": "alibaba",
    "kimi": "moonshot",
    "moonshot": "moonshot",
    "mistral": "mistral",
    "ministral": "mistral",
    "codestral": "mistral",
    "pixtral": "mistral",
    "llama": "meta",
    "command": "cohere",
    "jamba": "ai21",
    "minimax": "minimax",
    "glm": "zhipu",
}

SUPPLEMENTAL_PROVIDERS: dict[str, tuple[str, str, list[str]]] = {
    "xiaomi": ("Xiaomi", "#ff6900", [
        "MiMo-VL-7B-RL",
        "MiMo-7B-RL",
        "MiMo-7B-SFT",
        "MiMo-7B-Base",
        "MiMo-7B-RL-Zero",
    ]),
    "tencent": ("Tencent (Hunyuan)", "#0052d9", [
        "hunyuan-turbos-latest",
        "hunyuan-turbo-latest",
        "hunyuan-large",
        "hunyuan-standard",
        "hunyuan-lite",
    ]),
    "baidu": ("Baidu (ERNIE)", "#2932e1", [
        "ernie-4.5-turbo-vl",
        "ernie-4.5-turbo-128k",
        "ernie-4.5-turbo-32k",
        "ernie-4.5-turbo-8k",
        "ernie-x1-turbo-32k",
        "ernie-4.0-turbo-8k",
        "ernie-3.5-8k",
    ]),
    "iflytek": ("iFlytek (Spark)", "#e1251b", [
        "spark-x1",
        "spark-max-32k",
        "spark-max",
        "spark-pro-128k",
        "spark-pro",
        "spark-lite",
    ]),
    "huawei": ("Huawei (Pangu)", "#cf0a2c", [
        "pangu-ultra-moe",
        "pangu-pro-moe",
        "pangu-lite",
    ]),
    "sensetime": ("SenseTime", "#7c3aed", [
        "SenseNova-V6-5",
        "SenseNova-V6-Pro",
        "SenseNova-V6-Reasoner",
        "SenseNova-V5-5",
    ]),
}

MODEL_RELEASE_DATES = {
    "claude-opus-4.7": "2026-05-18",
    "claude-opus-4.6": "2026-03-03",
    "claude-sonnet-4.6": "2026-02-12",
    "claude-opus-4.5": "2025-11-24",
    "claude-sonnet-4.5": "2025-09-29",
    "claude-haiku-4.5": "2025-10-15",
    "claude-opus-4.1": "2025-08-05",
    "claude-opus-4": "2025-05-22",
    "claude-sonnet-4": "2025-05-22",
    "claude-3.5-haiku": "2024-10-22",
    "claude-3-haiku": "2024-03-07",
    "gpt-5.5": "2026-05-01",
    "gpt-5.4": "2026-04-01",
    "gpt-5.3": "2026-03-01",
    "gpt-5.2": "2026-02-01",
    "gpt-5.1": "2026-01-01",
    "gpt-5": "2025-08-07",
    "gpt-4.1": "2025-04-14",
    "gpt-4o": "2024-05-13",
    "o4-mini": "2025-04-16",
    "o3": "2025-04-16",
    "o3-mini": "2025-01-31",
    "o1": "2024-12-05",
    "deepseek-v4-pro": "2026-05-01",
    "deepseek-v4-flash": "2026-04-01",
    "deepseek-v3.2": "2025-12-01",
    "deepseek-v3.1": "2025-08-21",
    "deepseek-r1-0528": "2025-05-28",
    "deepseek-chat-v3-0324": "2025-03-24",
    "deepseek-r1": "2025-01-20",
    "MiMo-VL-7B-RL": "2025-05-01",
    "MiMo-7B-RL": "2025-04-30",
    "MiMo-7B-SFT": "2025-04-30",
    "MiMo-7B-Base": "2025-04-30",
    "MiMo-7B-RL-Zero": "2025-04-30",
}


def _color(pid: str) -> str:
    h = hashlib.md5(pid.encode()).hexdigest()
    return f"#{h[0:6]}"


def _allow_model(name: str) -> bool:
    lower = name.lower()
    for pat in MODEL_EXCLUDE_PATTERNS:
        if pat in lower:
            return False
    for prefix in MODEL_PREFIX_ALLOWLIST:
        if lower.startswith(prefix):
            return True
    return False


def _ensure_provider(providers: dict[str, dict], pid: str, name: str, color: str) -> dict:
    if pid not in providers:
        providers[pid] = {"id": pid, "name": name, "color": color, "models": {}}
    return providers[pid]


def _model_entry(name: str, pricing: dict | None = None, source: str | None = None) -> dict:
    entry = {"name": name}
    if pricing and pricing.get("input") is not None and pricing.get("output") is not None:
        entry["pricing"] = {
            "input": round(float(pricing["input"]), 8),
            "output": round(float(pricing["output"]), 8),
        }
        if source:
            entry["pricing_source"] = source
    return entry


def _has_complete_pricing(entry: dict) -> bool:
    pricing = entry.get("pricing") or {}
    return pricing.get("input") is not None and pricing.get("output") is not None


def _add_model(providers: dict[str, dict], raw_pid: str, model_name: str, pricing: dict | None = None, source: str | None = None) -> None:
    if raw_pid not in PROVIDER_WHITELIST or not _allow_model(model_name):
        return
    if not pricing or pricing.get("input") is None or pricing.get("output") is None:
        return
    canonical_id, display_name, color = PROVIDER_WHITELIST[raw_pid]
    models = _ensure_provider(providers, canonical_id, display_name, color)["models"]
    current = models.get(model_name)
    if current and _has_complete_pricing(current):
        return
    models[model_name] = _model_entry(model_name, pricing, source)



def load_existing():
    if not os.path.exists(MODELS_PATH):
        return {}
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _price_per_million(input_value, output_value, multiplier: int) -> dict | None:
    if input_value is None or output_value is None:
        return None
    try:
        return {
            "input": float(input_value) * multiplier,
            "output": float(output_value) * multiplier,
        }
    except (TypeError, ValueError):
        return None


def _entry_name(entry) -> str:
    return entry.get("name") if isinstance(entry, dict) else str(entry)


def _entry_from_existing(entry) -> dict:
    if isinstance(entry, dict):
        return entry
    return {"name": str(entry)}


def fetch_openrouter():
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
            pricing_raw = m.get("pricing") or {}
            pricing = _price_per_million(pricing_raw.get("prompt"), pricing_raw.get("completion"), 1_000_000)
            raw_pid, model_name = raw_id.split("/", 1)
            _add_model(providers, raw_pid, model_name, pricing, "openrouter")
        total = sum(len(p["models"]) for p in providers.values())
        print(f"  OpenRouter: {len(providers)} providers, {total} models")
    except Exception as e:
        print(f"  OpenRouter fetch failed: {e}")
    return providers


def fetch_litellm():
    providers: dict[str, dict] = {}
    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json",
            headers={"User-Agent": "TokenTracker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        for key, value in data.items():
            if "/" not in key or not isinstance(value, dict):
                continue
            pricing = _price_per_million(
                value.get("input_cost_per_token"),
                value.get("output_cost_per_token"),
                1_000_000,
            )
            raw_pid, model_name = key.split("/", 1)
            _add_model(providers, raw_pid, model_name, pricing, "litellm")
        total = sum(len(p["models"]) for p in providers.values())
        print(f"  LiteLLM: {len(providers)} providers, {total} models")
    except Exception as e:
        print(f"  LiteLLM fetch failed: {e}")
    return providers


def fetch_artificial_analysis():
    providers: dict[str, dict] = {}
    try:
        req = urllib.request.Request(
            "https://artificialanalysis.ai/models",
            headers={"User-Agent": "Mozilla/5.0 TokenTracker/1.0", "Accept": "text/html"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
        except http.client.IncompleteRead as e:
            raw = e.partial
        page = raw.decode("utf-8", "ignore")
        scripts = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S)
        for script in scripts:
            try:
                data = json.loads(html.unescape(script))
            except Exception:
                continue
            if not isinstance(data, dict) or "pricing" not in str(data.get("name", "")).lower():
                continue
            for item in data.get("data", []):
                if not isinstance(item, dict):
                    continue
                label = item.get("label") or ""
                details_url = item.get("detailsUrl") or ""
                model_name = details_url.rsplit("/", 1)[-1] if details_url else label
                prefix = model_name.split("-", 1)[0].lower()
                raw_pid = ARTIFICIAL_ANALYSIS_PREFIXES.get(prefix, prefix)
                prices = {
                    price.get("name"): price.get("value")
                    for price in item.get("pricing", [])
                    if isinstance(price, dict)
                }
                pricing = _price_per_million(prices.get("inputPrice"), prices.get("outputPrice"), 1)
                _add_model(providers, raw_pid, model_name, pricing, "artificial-analysis")
        total = sum(len(p["models"]) for p in providers.values())
        print(f"  Artificial Analysis: {len(providers)} providers, {total} models")
    except Exception as e:
        print(f"  Artificial Analysis fetch failed: {e}")
    return providers


def supplemental_providers():
    providers: dict[str, dict] = {}
    print("  Supplemental: skipped models without public input/output pricing")
    return providers


def _parse_date(name: str) -> tuple[int, int, int]:
    explicit = MODEL_RELEASE_DATES.get(name) or MODEL_RELEASE_DATES.get(name.lower())
    if explicit:
        return tuple(int(part) for part in explicit.split("-"))

    lower = name.lower()
    match = re.search(r"(20\d{2})[-_.]?(0[1-9]|1[0-2])[-_.]?([0-3]\d)", lower)
    if match:
        return tuple(int(part) for part in match.groups())

    match = re.search(r"(?<!\d)(\d{2})(0[1-9]|1[0-2])([0-3]\d)(?!\d)", lower)
    if match:
        year, month, day = (int(part) for part in match.groups())
        return (2000 + year, month, day)

    match = re.search(r"(?<!\d)(\d{2})(0[1-9]|1[0-2])(?!\d)", lower)
    if match:
        year, month = (int(part) for part in match.groups())
        return (2000 + year, month, 1)

    return (0, 0, 0)


def _parse_version(name: str) -> tuple[int, int, int, int]:
    lower = name.lower()
    version_match = re.search(r"(?:^|[-_.])(?:v|r)?(\d+)(?:[.-](\d+))?(?:[.-](\d+))?(?:[.-](\d+))?", lower)
    if not version_match:
        nums = re.findall(r"\d+", lower)
        version = tuple(int(n) for n in nums if int(n) < 2000)
    else:
        version = tuple(int(n) for n in version_match.groups(default="0"))
    while len(version) < 4:
        version = version + (0,)
    return version[:4]


def model_sort_key(name: str) -> tuple:
    lower = name.lower()
    deprecated = any(word in lower for word in ("deprecated", "legacy", "preview"))
    latest = any(word in lower for word in ("latest", "stable"))
    return (
        deprecated,
        tuple(-value for value in _parse_date(name)),
        tuple(-value for value in _parse_version(name)),
        not latest,
        len(name),
        lower,
    )


def clamp_models(models: list[str], max_per_provider: int = 40) -> list[str]:
    return sorted(models, key=model_sort_key)[:max_per_provider]


def main():
    print("Syncing model registry from OpenRouter + LiteLLM + Artificial Analysis...")

    existing = load_existing()
    existing_map: dict[str, dict] = {p["id"]: p for p in existing.get("providers", [])}

    source_providers = [fetch_openrouter(), fetch_litellm(), fetch_artificial_analysis(), supplemental_providers()]

    merged: dict[str, dict] = {}
    for source in source_providers:
        for pid, pdata in source.items():
            if pid in merged:
                for model_name, entry in pdata["models"].items():
                    if model_name not in merged[pid]["models"] or not _has_complete_pricing(merged[pid]["models"][model_name]):
                        merged[pid]["models"][model_name] = entry
            else:
                merged[pid] = pdata

    for pid, pdata in existing_map.items():
        if pid not in merged:
            merged[pid] = {
                "id": pid,
                "name": pdata.get("name", pid),
                "color": pdata.get("color", _color(pid)),
                "models": {
                    _entry_name(entry): _entry_from_existing(entry)
                    for entry in pdata.get("models", [])
                    if _has_complete_pricing(_entry_from_existing(entry))
                },
            }
        else:
            for entry in pdata.get("models", []):
                existing_entry = _entry_from_existing(entry)
                model_name = _entry_name(existing_entry)
                if _has_complete_pricing(existing_entry) and model_name not in merged[pid]["models"]:
                    merged[pid]["models"][model_name] = existing_entry

    result_providers = []
    for pid, pdata in merged.items():
        model_names = clamp_models(list(pdata["models"].keys()))
        models = [pdata["models"][name] for name in model_names if _has_complete_pricing(pdata["models"][name])]
        if not models:
            continue
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
        "source": "openrouter+lite-llm+artificial-analysis",
    }

    os.makedirs(os.path.dirname(MODELS_PATH), exist_ok=True)
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total_models = sum(len(p["models"]) for p in result_providers)
    print(f"Done: {len(result_providers)} providers, {total_models} models → {MODELS_PATH}")


if __name__ == "__main__":
    main()
