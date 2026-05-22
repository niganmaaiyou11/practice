"""
Build a merged seed_models.json from existing seed data and scraped category scores.
"""
import json
import os

# Scraped data from coding leaderboard page 1
CODING_SCORES = {
    "claude-mythos-preview": 57.3,
    "gpt-5.5": 53.1,
    "claude-opus-4-7": 51.6,
    "claude-opus-4-6": 45.6,
    "kimi-k2.6": 45.6,
    "glm-5.1": 45.1,
    "deepseek-v4-pro-max": 45.0,
    "gpt-5.4": 44.3,
    "gemini-3.1-pro-preview": 44.1,
    "gpt-5.3-codex": 43.9,
    "qwen3.6-plus": 43.3,
    "claude-opus-4-5-20251101": 41.0,
    "gpt-5.2-codex": 40.2,
    "minimax-m2.7": 40.1,
    "minimax-m2.5": 38.9,
    "deepseek-v4-flash-max": 38.8,
    "claude-sonnet-4-6": 37.7,
    "glm-5": 37.3,
    "gpt-5.2-2025-12-11": 35.7,
    "qwen3.6-27b": 35.5,
    "mimo-v2-pro": 35.4,
    "gpt-5.4-mini": 35.4,
    "gpt-5-2025-08-07": 34.5,
    "gemini-3-pro-preview": 33.4,
    "seed-2.0-pro": 33.3,
    "minicpm-sala": 33.1,
    "muse-spark": 32.9,
    "kimi-k2.5": 32.5,
    "claude-sonnet-4-5-20250929": 32.0,
    "gpt-5.1-2025-11-13": 31.8,
}

# Scraped data from reasoning leaderboard page 1
REASONING_SCORES = {
    "claude-mythos-preview": 71.3,
    "gpt-5.5": 62.9,
    "claude-opus-4-7": 62.6,
    "gpt-5.5-pro": 61.9,
    "claude-opus-4-6": 60.0,
    "kimi-k2.6": 59.1,
    "gemini-3.1-pro-preview": 59.0,
    "gpt-5.4": 58.0,
    "deepseek-v4-pro-max": 57.8,
    "gpt-5.2-pro-2025-12-11": 57.3,
    "gpt-5.3-codex": 56.2,
    "glm-5.1": 55.1,
    "seed-2.0-pro": 54.6,
    "claude-opus-4-5-20251101": 54.5,
    "grok-4-heavy": 54.2,
    "gpt-5.2-2025-12-11": 54.1,
    "gpt-5.1-high-2025-11-12": 53.7,
    "minimax-m2.7": 53.6,
    "minimax-m2.5": 53.2,
    "qwen3.6-plus": 53.0,
    "muse-spark": 52.9,
    "gpt-5.2-codex": 52.7,
    "claude-sonnet-4-6": 52.6,
    "deepseek-v4-flash-max": 52.2,
    "glm-5": 52.2,
    "mimo-v2-pro": 52.1,
    "kimi-k2.5": 50.5,
    "gemini-3-pro-preview": 50.1,
    "step-3.5-flash": 49.9,
    "gemini-3-flash-preview": 49.5,
}

# Scraped data from writing leaderboard page 1
WRITING_SCORES = {
    "claude-opus-4-6": 44.6,
    "longcat-flash-thinking-2601": 38.1,
    "claude-opus-4-5-20251101": 35.6,
    "claude-sonnet-4-6": 35.6,
    "gpt-5.4": 35.5,
    "claude-sonnet-4-5-20250929": 35.3,
    "hermes-3-70b": 34.8,
    "gpt-5.2-2025-12-11": 33.1,
    "qwen-2.5-72b-instruct": 31.0,
    "gpt-5.5": 30.8,
    "gpt-5-2025-08-07": 29.6,
    "qwen3.5-397b-a17b": 28.7,
    "gpt-5.1-2025-11-13": 28.4,
    "mimo-v2-pro": 28.4,
    "llama-3.3-nemotron-super-49b-v1": 27.8,
    "gpt-5.1-instant-2025-11-12": 26.9,
    "step3-vl-10b": 26.7,
    "gpt-5.1-thinking-2025-11-12": 25.5,
    "claude-sonnet-4-20250514": 25.4,
    "claude-haiku-4-5-20251001": 25.3,
    "glm-4.5": 25.2,
    "glm-4.5-air": 25.1,
    "claude-opus-4-20250514": 25.1,
    "claude-opus-4-1-20250805": 24.8,
    "deepseek-v2.5": 24.5,
    "qwen3.5-122b-a10b": 24.3,
    "longcat-flash-thinking": 23.8,
    "claude-3-7-sonnet-20250219": 23.8,
    "o3-2025-04-16": 23.0,
    "qwen3.5-27b": 22.3,
}


def build():
    # Load existing seed data
    seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "seed_models.json")
    with open(seed_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    # Index existing models by slug
    existing_by_slug = {}
    for m in existing:
        slug = m.get("id", "")
        existing_by_slug[slug] = m

    # Merge category scores into existing models
    all_slugs = set()
    all_slugs.update(CODING_SCORES.keys())
    all_slugs.update(REASONING_SCORES.keys())
    all_slugs.update(WRITING_SCORES.keys())

    updated_count = 0
    for slug in all_slugs:
        if slug in existing_by_slug:
            model = existing_by_slug[slug]
            scores = model.setdefault("scores", {})

            if slug in CODING_SCORES and "coding" not in scores:
                scores["coding"] = CODING_SCORES[slug]
                updated_count += 1
            if slug in REASONING_SCORES and "reasoning" not in scores:
                scores["reasoning"] = REASONING_SCORES[slug]
                updated_count += 1
            if slug in WRITING_SCORES and "writing" not in scores:
                scores["writing"] = WRITING_SCORES[slug]
                updated_count += 1

            # Recalculate overall_score from available category scores
            cat_vals = []
            for cat in ["coding", "reasoning", "writing", "math"]:
                v = scores.get(cat)
                if v is not None:
                    cat_vals.append(v)
            if cat_vals:
                model["overall_score"] = round(sum(cat_vals) / len(cat_vals), 1)

    # Override scores with fresh scraped data (more up-to-date)
    overridden = 0
    for slug in all_slugs:
        if slug in existing_by_slug:
            model = existing_by_slug[slug]
            scores = model.setdefault("scores", {})

            if slug in CODING_SCORES:
                old = scores.get("coding")
                new = CODING_SCORES[slug]
                if old != new:
                    scores["coding"] = new
                    overridden += 1
            if slug in REASONING_SCORES:
                old = scores.get("reasoning")
                new = REASONING_SCORES[slug]
                if old != new:
                    scores["reasoning"] = new
                    overridden += 1
            if slug in WRITING_SCORES:
                old = scores.get("writing")
                new = WRITING_SCORES[slug]
                if old != new:
                    scores["writing"] = new
                    overridden += 1

            # Recalculate overall_score
            cat_vals = []
            for cat in ["coding", "reasoning", "writing", "math"]:
                v = scores.get(cat)
                if v is not None:
                    cat_vals.append(v)
            if cat_vals:
                model["overall_score"] = round(sum(cat_vals) / len(cat_vals), 1)

    # Save updated seed
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated_count} new scores, overridden {overridden} existing scores")

    # Print stats
    has_coding = sum(1 for m in existing if m.get("scores", {}).get("coding") is not None)
    has_reasoning = sum(1 for m in existing if m.get("scores", {}).get("reasoning") is not None)
    has_writing = sum(1 for m in existing if m.get("scores", {}).get("writing") is not None)
    print(f"Models: {len(existing)}")
    print(f"  with coding: {has_coding}")
    print(f"  with reasoning: {has_reasoning}")
    print(f"  with writing: {has_writing}")


if __name__ == "__main__":
    build()
