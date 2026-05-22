"""
Build comprehensive SEED_MODELS from real llm-stats.com data.
Data sourced from 4 category leaderboard pages via browser scraping.
"""
import json

# ── Raw data from 4 category pages ──────────────────────────
# Format: (slug, name, provider, score, [price, context, speed])

coding_data = [
    ("claude-mythos-preview","Claude Mythos Preview","Anthropic",57.3,None,None,None),
    ("gpt-5.5","GPT-5.5","OpenAI",53.1,10,1100000,31),
    ("claude-opus-4-7","Claude Opus 4.7","Anthropic",51.6,9,1000000,48),
    ("claude-opus-4-6","Claude Opus 4.6","Anthropic",45.6,9,1000000,102),
    ("kimi-k2.6","Kimi K2.6","Moonshot AI",45.6,1.56,262100,239),
    ("glm-5.1","GLM-5.1","Zhipu AI",45.1,2,200000,340),
    ("deepseek-v4-pro-max","DeepSeek-V4-Pro-Max","DeepSeek",45.0,2.09,1000000,76),
    ("gpt-5.4","GPT-5.4","OpenAI",44.3,5,1000000,110),
    ("gemini-3.1-pro-preview","Gemini 3.1 Pro","Google",44.1,5,1000000,212),
    ("gpt-5.3-codex","GPT-5.3 Codex","OpenAI",43.9,4.2,400000,205),
    ("qwen3.6-plus","Qwen3.6 Plus","Alibaba",43.3,1,1000000,70),
    ("claude-opus-4-5-20251101","Claude Opus 4.5","Anthropic",41.0,9,200000,248),
    ("gpt-5.2-codex","GPT-5.2 Codex","OpenAI",40.2,4.2,400000,224),
    ("minimax-m2.7","MiniMax M2.7","MiniMax",40.1,0.48,204800,251),
    ("minimax-m2.5","MiniMax M2.5","MiniMax",38.9,0.48,1000000,513),
    ("deepseek-v4-flash-max","DeepSeek-V4-Flash-Max","DeepSeek",38.8,0.17,1000000,165),
    ("claude-sonnet-4-6","Claude Sonnet 4.6","Anthropic",37.7,5.4,200000,221),
    ("glm-5","GLM-5","Zhipu AI",37.3,1.44,200000,263),
    ("gpt-5.2-2025-12-11","GPT-5.2","OpenAI",35.7,4.2,400000,231),
    ("qwen3.6-27b","Qwen3.6-27B","Alibaba",35.5,1.2,262100,131),
    ("mimo-v2-pro","MiMo-V2-Pro","MiMo",35.4,None,None,None),
    ("gpt-5.4-mini","GPT-5.4 mini","OpenAI",35.4,1.5,400000,377),
    ("gpt-5-2025-08-07","GPT-5","OpenAI",34.5,None,None,None),
    ("gemini-3-pro-preview","Gemini 3 Pro","Google",33.4,None,None,None),
    ("seed-2.0-pro","Seed 2.0 Pro","ByteDance",33.3,None,None,None),
    ("minicpm-sala","MiniCPM-SALA","OpenBMB",33.1,None,None,None),
    ("muse-spark","Muse Spark","Muse",32.9,None,None,None),
    ("kimi-k2.5","Kimi K2.5","Moonshot AI",32.5,None,None,None),
    ("claude-sonnet-4-5-20250929","Claude Sonnet 4.5","Anthropic",32.0,5.4,200000,186),
    ("gpt-5.1-2025-11-13","GPT-5.1","OpenAI",31.8,3,400000,528),
]

math_data = [
    ("claude-mythos-preview","Claude Mythos Preview","Anthropic",61.7),
    ("muse-spark","Muse Spark","Muse",55.2),
    ("gemini-3.1-pro-preview","Gemini 3.1 Pro","Google",54.8),
    ("deepseek-v4-pro-max","DeepSeek-V4-Pro-Max","DeepSeek",53.8),
    ("grok-4-heavy","Grok-4 Heavy","xAI",53.5),
    ("claude-opus-4-6","Claude Opus 4.6","Anthropic",52.4),
    ("claude-opus-4-7","Claude Opus 4.7","Anthropic",52.2),
    ("gemini-3-pro-preview","Gemini 3 Pro","Google",51.6),
    ("gpt-5.5-pro","GPT-5.5 Pro","OpenAI",51.6),
    ("deepseek-v4-flash-max","DeepSeek-V4-Flash-Max","DeepSeek",51.5),
    ("gpt-5.2-pro-2025-12-11","GPT-5.2 Pro","OpenAI",51.3),
    ("gemini-3-flash-preview","Gemini 3 Flash","Google",50.7),
    ("kimi-k2.6","Kimi K2.6","Moonshot AI",50.7),
    ("gpt-5.2-2025-12-11","GPT-5.2","OpenAI",50.4),
    ("qwen3.6-plus","Qwen3.6 Plus","Alibaba",49.8),
    ("gpt-5.5","GPT-5.5","OpenAI",48.6),
    ("kimi-k2.5","Kimi K2.5","Moonshot AI",47.9),
    ("gpt-5.1-high-2025-11-12","GPT-5.1 High","OpenAI",47.8),
    ("kimi-k2-thinking-0905","Kimi K2-Thinking","Moonshot AI",47.3),
    ("gpt-5.4","GPT-5.4","OpenAI",47.3),
    ("glm-5.1","GLM-5.1","Zhipu AI",47.2),
    ("step-3.5-flash","Step-3.5-Flash","StepFun",47.1),
    ("qwen3.5-397b-a17b","Qwen3.5-397B","Alibaba",46.7),
    ("deepseek-v3.2-speciale","DeepSeek-V3.2-Speciale","DeepSeek",46.2),
    ("gpt-oss-20b-high","GPT OSS 20B High","OpenAI",45.7),
    ("seed-2.0-pro","Seed 2.0 Pro","ByteDance",45.3),
    ("gpt-5.1-medium-2025-11-12","GPT-5.1 Medium","OpenAI",44.5),
    ("qwen3.5-122b-a10b","Qwen3.5-122B","Alibaba",44.4),
    ("claude-sonnet-4-6","Claude Sonnet 4.6","Anthropic",44.2),
    ("glm-4.7","GLM-4.7","Zhipu AI",44.1),
]

reasoning_data = [
    ("claude-mythos-preview","Claude Mythos Preview","Anthropic",71.3),
    ("gpt-5.5","GPT-5.5","OpenAI",63.1),
    ("claude-opus-4-7","Claude Opus 4.7","Anthropic",62.8),
    ("gpt-5.5-pro","GPT-5.5 Pro","OpenAI",62.0),
    ("claude-opus-4-6","Claude Opus 4.6","Anthropic",60.0),
    ("kimi-k2.6","Kimi K2.6","Moonshot AI",59.4),
    ("gemini-3.1-pro-preview","Gemini 3.1 Pro","Google",59.1),
    ("gpt-5.4","GPT-5.4","OpenAI",58.0),
    ("deepseek-v4-pro-max","DeepSeek-V4-Pro-Max","DeepSeek",57.7),
    ("gpt-5.2-pro-2025-12-11","GPT-5.2 Pro","OpenAI",56.5),
    ("gpt-5.3-codex","GPT-5.3 Codex","OpenAI",56.1),
    ("glm-5.1","GLM-5.1","Zhipu AI",55.3),
    ("claude-opus-4-5-20251101","Claude Opus 4.5","Anthropic",54.6),
    ("seed-2.0-pro","Seed 2.0 Pro","ByteDance",54.5),
    ("gpt-5.2-2025-12-11","GPT-5.2","OpenAI",54.3),
    ("gpt-5.1-high-2025-11-12","GPT-5.1 High","OpenAI",53.9),
    ("minimax-m2.7","MiniMax M2.7","MiniMax",53.5),
    ("grok-4-heavy","Grok-4 Heavy","xAI",53.3),
    ("minimax-m2.5","MiniMax M2.5","MiniMax",52.8),
    ("muse-spark","Muse Spark","Muse",52.8),
    ("claude-sonnet-4-6","Claude Sonnet 4.6","Anthropic",52.6),
    ("gpt-5.2-codex","GPT-5.2 Codex","OpenAI",52.6),
    ("deepseek-v4-flash-max","DeepSeek-V4-Flash-Max","DeepSeek",52.2),
    ("qwen3.6-plus","Qwen3.6 Plus","Alibaba",52.2),
    ("glm-5","GLM-5","Zhipu AI",52.1),
    ("mimo-v2-pro","MiMo-V2-Pro","MiMo",51.7),
    ("kimi-k2.5","Kimi K2.5","Moonshot AI",50.5),
    ("gpt-5.1-2025-11-13","GPT-5.1","OpenAI",50.1),
    ("gemini-3-pro-preview","Gemini 3 Pro","Google",50.0),
    ("step-3.5-flash","Step-3.5-Flash","StepFun",49.8),
]

writing_data = [
    ("claude-opus-4-6","Claude Opus 4.6","Anthropic",44.6),
    ("longcat-flash-thinking-2601","LongCat-Flash-Thinking","LongCat",38.1),
    ("claude-opus-4-5-20251101","Claude Opus 4.5","Anthropic",35.6),
    ("claude-sonnet-4-6","Claude Sonnet 4.6","Anthropic",35.6),
    ("gpt-5.4","GPT-5.4","OpenAI",35.5),
    ("claude-sonnet-4-5-20250929","Claude Sonnet 4.5","Anthropic",35.3),
    ("hermes-3-70b","Hermes 3 70B","Nous Research",34.8),
    ("gpt-5.2-2025-12-11","GPT-5.2","OpenAI",33.1),
    ("qwen-2.5-72b-instruct","Qwen2.5 72B Instruct","Alibaba",31.0),
    ("gpt-5.5","GPT-5.5","OpenAI",30.8),
    ("gpt-5-2025-08-07","GPT-5","OpenAI",29.6),
    ("qwen3.5-397b-a17b","Qwen3.5-397B","Alibaba",28.7),
    ("gpt-5.1-2025-11-13","GPT-5.1","OpenAI",28.4),
    ("mimo-v2-pro","MiMo-V2-Pro","MiMo",28.4),
    ("llama-3.3-nemotron-super-49b-v1","Llama 3.3 Nemotron Super 49B","Meta",27.8),
    ("gpt-5.1-instant-2025-11-12","GPT-5.1 Instant","OpenAI",26.9),
    ("step3-vl-10b","Step3-VL-10B","StepFun",26.7),
    ("gpt-5.1-thinking-2025-11-12","GPT-5.1 Thinking","OpenAI",25.5),
    ("claude-sonnet-4-20250514","Claude Sonnet 4","Anthropic",25.4),
    ("claude-haiku-4-5-20251001","Claude Haiku 4.5","Anthropic",25.3),
    ("glm-4.5","GLM-4.5","Zhipu AI",25.2),
    ("glm-4.5-air","GLM-4.5-Air","Zhipu AI",25.1),
    ("claude-opus-4-20250514","Claude Opus 4","Anthropic",25.1),
    ("claude-opus-4-1-20250805","Claude Opus 4.1","Anthropic",24.8),
    ("deepseek-v2.5","DeepSeek-V2.5","DeepSeek",24.5),
    ("qwen3.5-122b-a10b","Qwen3.5-122B","Alibaba",24.3),
    ("longcat-flash-thinking","LongCat-Flash-Thinking","LongCat",23.8),
    ("claude-3-7-sonnet-20250219","Claude 3.7 Sonnet","Anthropic",23.8),
    ("o3-2025-04-16","o3","OpenAI",23.0),
    ("qwen3.5-27b","Qwen3.5-27B","Alibaba",22.3),
]

# ── Merge into unified dataset ──────────────────────────────
merged = {}

for slug, name, prov, score, *rest in coding_data:
    merged[slug] = {
        "name": name, "provider": prov,
        "coding": score, "math": None, "reasoning": None, "writing": None,
        "price": rest[0] if rest else None,
        "context": rest[1] if len(rest) > 1 else None,
        "speed": rest[2] if len(rest) > 2 else None,
    }

def merge_list(data, key):
    for slug, name, prov, score in data:
        if slug in merged:
            merged[slug][key] = score
        else:
            merged[slug] = {
                "name": name, "provider": prov,
                "coding": None, "math": None, "reasoning": None, "writing": None,
                "price": None, "context": None, "speed": None,
                key: score,
            }

merge_list(math_data, "math")
merge_list(reasoning_data, "reasoning")
merge_list(writing_data, "writing")

# Compute overall = average of available category scores (equal weight)
for slug, m in merged.items():
    scores = [s for s in [m["coding"], m["math"], m["reasoning"], m["writing"]] if s is not None]
    m["overall"] = round(sum(scores) / len(scores), 1) if scores else None

# Sort by overall score descending
sorted_models = sorted(merged.items(), key=lambda x: x[1]["overall"] or 0, reverse=True)

print(f"Total unique models: {len(merged)}")
complete = sum(1 for _, m in merged.items() if all(
    m[k] is not None for k in ["coding", "math", "reasoning", "writing"]))
print(f"Models with all 4 scores: {complete}")
print()

# Print top 50
for i, (slug, m) in enumerate(sorted_models[:50]):
    parts = []
    for k in ["coding", "math", "reasoning", "writing"]:
        if m[k] is not None:
            parts.append(f"{k[:4]}:{m[k]:.1f}")
    print(f'{i+1:2d}. {m["name"]:35s} ({m["provider"]:15s}) Overall:{m["overall"]:5.1f}  [{", ".join(parts)}]')

# ── Generate Python SEED_MODELS code ─────────────────────────
print("\n\n# ── Generated SEED_MODELS ──")
print("SEED_MODELS = [")
for i, (slug, m) in enumerate(sorted_models):
    scores = {}
    if m["coding"] is not None:
        scores["coding"] = m["coding"]
    if m["math"] is not None:
        scores["math"] = m["math"]
    if m["reasoning"] is not None:
        scores["reasoning"] = m["reasoning"]
    if m["writing"] is not None:
        scores["writing"] = m["writing"]

    pricing = {}
    if m["price"] is not None:
        pricing["input"] = m["price"]

    ctx = m["context"] or 128000
    speed = m["speed"] or 50

    print(f'    {{"id":"{slug}","name":"{m["name"]}","provider":{{"id":"{m["provider"].lower()}","name":"{m["provider"]}"}},"scores":{json.dumps(scores)},"overall_score":{m["overall"]},"tokens_per_second":{speed},"pricing":{json.dumps(pricing)},"context_window":{ctx},"max_output_tokens":{ctx//8},"knowledge_cutoff":"2025-12","modalities":["text"]}},')

print("]")
