"""
Update seed JSON files with real LLM STATS scores scraped from llm-stats.com homepage.
Run after scrape_homepage_llm_stats.py or when LLM_STATS_DATA is updated.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# LLM STATS data scraped from https://llm-stats.com homepage table (May 2026)
# Format: "ModelNameProvider" -> llm_stats_score
LLM_STATS_DATA = {
    "Claude Mythos PreviewAnthropic": 70.3,
    "GPT-5.5OpenAI": 64.3,
    "Claude Opus 4.7Anthropic": 61.3,
    "GPT-5.4OpenAI": 61.3,
    "GPT-5.2 ProOpenAI": 61.2,
    "Kimi K2.6Moonshot AI": 59.0,
    "Gemini 3.1 ProGoogle": 58.0,
    "Claude Opus 4.6Anthropic": 57.7,
    "Seed 2.0 ProByteDance": 57.0,
    "Gemini 3 ProGoogle": 56.5,
    "GPT-5.2OpenAI": 56.3,
    "GPT-5.1 ThinkingOpenAI": 54.9,
    "Gemini 3 FlashGoogle": 54.6,
    "GPT-5.1OpenAI": 54.3,
    "GPT-5.1 HighOpenAI": 53.6,
    "Muse SparkMeta": 53.1,
    "Qwen3.6 PlusAlibaba Cloud / Qwen Team": 52.1,
    "GPT-5.1 InstantOpenAI": 52.1,
    "GPT-5 MediumOpenAI": 52.0,
    "DeepSeek-V4-Pro-MaxDeepSeek": 52.0,
    "Claude Sonnet 4.6Anthropic": 50.9,
    "GPT-5OpenAI": 50.4,
    "Qwen3.5-397B-A17BAlibaba Cloud / Qwen Team": 49.9,
    "GPT-5 HighOpenAI": 49.5,
    "Step-3.5-FlashStepFun": 49.3,
    "Claude Opus 4.5Anthropic": 49.2,
    "GPT-5.4 miniOpenAI": 49.0,
    "Kimi K2.5Moonshot AI": 48.6,
    "Grok-4 HeavyxAI": 48.5,
    "GLM-5.1Zhipu AI": 46.8,
    "ERNIE 5.0Baidu": 46.6,
    "Grok 4 FastxAI": 46.1,
    "Gemini 3.1 Flash-LiteGoogle": 45.6,
    "GLM-4.7Zhipu AI": 45.1,
    "GPT-5.5 InstantOpenAI": 44.6,
    "Qwen3.6-27BAlibaba Cloud / Qwen Team": 44.4,
    "Kimi K2-Thinking-0905Moonshot AI": 44.4,
    "Grok-4xAI": 44.3,
    "Qwen3.5-122B-A10BAlibaba Cloud / Qwen Team": 44.2,
    "MiniMax M2.7MiniMax": 44.1,
    "GLM-5V-TurboZhipu AI": 43.8,
    "Seed 2.0 LiteByteDance": 43.6,
    "Gemma 4 31BGoogle": 43.4,
    "DeepSeek-V3.2 (Thinking)DeepSeek": 43.3,
    "GPT-5.3 CodexOpenAI": 43.0,
    "DeepSeek-V3.2DeepSeek": 42.8,
    "Grok-3 MinixAI": 42.5,
    "DeepSeek-V4-Flash-MaxDeepSeek": 42.1,
    "Claude Opus 4.1Anthropic": 42.0,
    "o3OpenAI": 41.7,
    "Gemini 2.5 Pro Preview 06-05Google": 41.3,
    "Qwen3.5-27BAlibaba Cloud / Qwen Team": 41.3,
    "DeepSeek-V3.2-ExpDeepSeek": 41.1,
    "ChatGPT-4o LatestOpenAI": 41.0,
    "MiMo-V2-ProXiaomi": 40.9,
    "Qwen3.6-35B-A3BAlibaba Cloud / Qwen Team": 40.7,
    "GPT-5.4 nanoOpenAI": 40.5,
    "MiniMax M2.1MiniMax": 40.4,
    "DeepSeek-R1-0528DeepSeek": 39.7,
    "Grok-3xAI": 39.3,
    "GLM-4.6Zhipu AI": 39.1,
    "LongCat-Flash-Thinking-2601Meituan": 38.9,
    "MiMo-V2-OmniXiaomi": 38.8,
    "Claude Sonnet 4.5Anthropic": 37.9,
    "GLM-4.5Zhipu AI": 37.6,
    "Qwen3.5-35B-A3BAlibaba Cloud / Qwen Team": 37.3,
    "Gemini 2.5 ProGoogle": 37.0,
    "Nemotron 3 Super (120B A12B)NVIDIA": 36.9,
    "Claude Opus 4Anthropic": 36.4,
    "MiMo-V2-FlashXiaomi": 36.3,
    "GPT-5 miniOpenAI": 36.1,
    "Qwen3-235B-A22B-Thinking-2507Alibaba Cloud / Qwen Team": 35.6,
    "Claude 3.7 SonnetAnthropic": 35.4,
    "o4-miniOpenAI": 35.2,
    "Gemma 4 26B-A4BGoogle": 34.8,
    "MiniMax M2MiniMax": 34.5,
    "Qwen3 VL 235B A22B ThinkingAlibaba Cloud / Qwen Team": 34.2,
    "LongCat-Flash-ThinkingMeituan": 33.8,
    "K-EXAONE-236B-A23BLG AI Research": 32.6,
    "GLM-4.5-AirZhipu AI": 31.8,
    "DeepSeek-V3.1DeepSeek": 31.8,
    "o1OpenAI": 31.5,
    "GLM-4.7-FlashZhipu AI": 31.2,
    "o1-proOpenAI": 31.2,
    "GPT OSS 120B HighOpenAI": 31.1,
    "Qwen3-235B-A22B-Instruct-2507Alibaba Cloud / Qwen Team": 31.0,
    "GPT OSS 120BOpenAI": 30.2,
    "Step3-VL-10BStepFun": 30.1,
    "Qwen3-Next-80B-A3B-ThinkingAlibaba Cloud / Qwen Team": 29.9,
    "Kimi K2 0905Moonshot AI": 29.6,
    "Qwen3 VL 235B A22B InstructAlibaba Cloud / Qwen Team": 29.5,
    "Mercury 2Inception": 29.2,
    "Qwen3 VL 32B ThinkingAlibaba Cloud / Qwen Team": 28.3,
    "Gemini 2.5 FlashGoogle": 28.2,
    "o3-miniOpenAI": 28.1,
    "Sarvam-105BSarvam AI": 28.1,
    "Claude Sonnet 4Anthropic": 27.8,
    "GPT-4.5OpenAI": 27.7,
    "Gemini 2.0 Flash ThinkingGoogle": 27.2,
    "Qwen3.5-9BAlibaba Cloud / Qwen Team": 26.8,
    "Qwen3-Next-80B-A3B-InstructAlibaba Cloud / Qwen Team": 26.6,
    "Kimi K2 InstructMoonshot AI": 25.8,
    "Kimi K2-Instruct-0905Moonshot AI": 25.8,
    "o1-previewOpenAI": 25.2,
    "Llama 3.1 Nemotron Ultra 253B v1NVIDIA": 25.1,
    "MiniMax M1 80KMiniMax": 24.8,
    "Qwen3 MaxAlibaba Cloud / Qwen Team": 24.4,
    "GPT-4.1OpenAI": 24.4,
    "GPT OSS 20B HighOpenAI": 24.1,
    "Claude Haiku 4.5Anthropic": 23.2,
    "MiniMax M1 40KMiniMax": 23.1,
    "Nemotron Nano 9B v2NVIDIA": 22.9,
    "LongCat-Flash-ChatMeituan": 22.7,
    "Qwen3-Coder 480B A35B InstructAlibaba Cloud / Qwen Team": 22.6,
    "Ministral 3 (14B Reasoning 2512)Mistral AI": 22.5,
    "Nemotron 3 Nano (30B A3B)NVIDIA": 22.0,
    "Qwen3 VL 32B InstructAlibaba Cloud / Qwen Team": 21.2,
    "Qwen3 VL 30B A3B ThinkingAlibaba Cloud / Qwen Team": 20.7,
    "Qwen3 32BAlibaba Cloud / Qwen Team": 19.8,
    "Qwen3.5-4BAlibaba Cloud / Qwen Team": 19.6,
    "Claude 3.5 SonnetAnthropic": 19.3,
    "DeepSeek-V3 0324DeepSeek": 18.6,
    "Sarvam-30BSarvam AI": 18.5,
    "GPT-5 nanoOpenAI": 18.3,
    "DeepSeek-V3DeepSeek": 18.3,
    "DeepSeek R1 ZeroDeepSeek": 18.2,
    "Kimi-k1.5Moonshot AI": 18.0,
    "Ministral 3 (8B Reasoning 2512)Mistral AI": 17.8,
    "Qwen3 30B A3BAlibaba Cloud / Qwen Team": 17.4,
    "Qwen3 VL 8B ThinkingAlibaba Cloud / Qwen Team": 17.0,
    "Qwen3 VL 30B A3B InstructAlibaba Cloud / Qwen Team": 16.9,
    "Mistral Small 4Mistral AI": 16.9,
    "Kimi K2 BaseMoonshot AI": 16.7,
    "Magistral MediumMistral AI": 16.6,
    "Llama 3.1 405B InstructMeta": 16.0,
    "Qwen3 235B A22BAlibaba Cloud / Qwen Team": 15.9,
    "DeepSeek R1 Distill Llama 70BDeepSeek": 15.9,
    "GPT OSS 20BOpenAI": 15.8,
    "GPT-4.1 miniOpenAI": 15.6,
    "Phi 4 Reasoning PlusMicrosoft": 15.4,
    "Llama 3.3 70B InstructMeta": 15.3,
    "Llama 4 MaverickMeta": 14.8,
    "Magistral Small 2506Mistral AI": 14.8,
    "Gemini 2.0 FlashGoogle": 14.7,
    "GPT-4oOpenAI": 14.7,
    "LongCat-Flash-LiteMeituan": 14.6,
    "QwQ-32BAlibaba Cloud / Qwen Team": 14.4,
    "DeepSeek R1 Distill Qwen 32BDeepSeek": 14.2,
    "Llama-3.3 Nemotron Super 49B v1NVIDIA": 13.4,
    "Gemini 1.5 ProGoogle": 13.3,
    "Grok-2xAI": 12.7,
    "Qwen3 VL 4B ThinkingAlibaba Cloud / Qwen Team": 12.7,
    "Phi 4 ReasoningMicrosoft": 12.0,
    "QwQ-32B-PreviewAlibaba Cloud / Qwen Team": 11.9,
    "GPT-5.5 ProOpenAI": 11.8,
    "QvQ-72B-PreviewAlibaba Cloud / Qwen Team": 11.6,
    "Qwen3 VL 8B InstructAlibaba Cloud / Qwen Team": 11.6,
    "Nova ProAmazon": 11.3,
    "DeepSeek R1 Distill Qwen 14BDeepSeek": 11.3,
    "Qwen2.5 72B InstructAlibaba Cloud / Qwen Team": 11.0,
    "Gemma 4 E4BGoogle": 10.9,
    "Mistral Large 3 (675B Instruct 2512 NVFP4)Mistral AI": 9.6,
    "Claude 3 OpusAnthropic": 9.3,
    "Grok-2 minixAI": 9.2,
    "o1-miniOpenAI": 8.9,
    "Mistral Large 3 (675B Instruct 2512)Mistral AI": 8.8,
    "Gemini 2.5 Flash-LiteGoogle": 8.7,
    "Mistral Large 3 (675B Base)Mistral AI": 8.5,
    "Gemini 2.0 Flash-LiteGoogle": 8.3,
    "Mistral Large 3 (675B Instruct 2512 Eagle)Mistral AI": 8.3,
    "Qwen2.5 VL 72B InstructAlibaba Cloud / Qwen Team": 7.6,
    "Qwen3 VL 4B InstructAlibaba Cloud / Qwen Team": 7.6,
    "Llama 3.1 70B InstructMeta": 7.5,
    "GPT-4 TurboOpenAI": 7.1,
    "MiniCPM-SALAOpenBMB": 6.5,
    "Pixtral LargeMistral AI": 5.9,
    "Nova LiteAmazon": 5.1,
    "Gemini 1.5 FlashGoogle": 4.5,
    "Llama 3.2 90B InstructMeta": 4.4,
    "Llama 4 ScoutMeta": 4.3,
    "Qwen2.5 32B InstructAlibaba Cloud / Qwen Team": 4.1,
    "Gemma 3 27BGoogle": 4.0,
    "DeepSeek R1 Distill Llama 8BDeepSeek": 3.9,
    "Mistral Large 2Mistral AI": 3.9,
    "Hermes 3 70BNous Research": 3.6,
    "DeepSeek R1 Distill Qwen 7BDeepSeek": 3.2,
    "Qwen2.5 VL 32B InstructAlibaba Cloud / Qwen Team": 3.1,
    "Phi 4Microsoft": 3.0,
    "Mistral Large 3Mistral AI": 2.7,
    "DeepSeek-V2.5DeepSeek": 2.6,
    "Phi 4 Mini ReasoningMicrosoft": 2.5,
    "Mistral Small 3.2 24B InstructMistral AI": 2.5,
    "Gemma 4 E2BGoogle": 2.2,
    "Mistral Small 3 24B InstructMistral AI": 1.9,
    "Mistral Small 3.1 24B InstructMistral AI": 1.5,
    "Qwen2 72B InstructAlibaba Cloud / Qwen Team": 0.9,
    "Qwen2-VL-72B-InstructAlibaba Cloud / Qwen Team": 0.7,
    "GPT-4OpenAI": 0.3,
    "Gemma 3 12BGoogle": 0.2,
    "Llama 3.1 Nemotron Nano 8B V1NVIDIA": 0.1,
    "Nova MicroAmazon": 0.1,
    "GPT-4.1 nanoOpenAI": -0.5,
    "Qwen2.5 14B InstructAlibaba Cloud / Qwen Team": -0.7,
    "GPT-4o miniOpenAI": -0.8,
    "Phi-3.5-MoE-instructMicrosoft": -1.0,
    "Mistral Small 3 24B BaseMistral AI": -1.6,
    "MiniMax M2.5MiniMax": -1.7,
    "Jamba 1.5 LargeAI21 Labs": -1.7,
    "Gemini 1.5 Flash 8BGoogle": -1.8,
    "Codestral-22BMistral AI": -1.9,
    "Mistral Small 3.1 24B BaseMistral AI": -2.0,
    "Claude 3 SonnetAnthropic": -2.5,
    "Gemma 2 27BGoogle": -2.5,
    "Qwen2.5 VL 7B InstructAlibaba Cloud / Qwen Team": -2.6,
    "Qwen2.5 7B InstructAlibaba Cloud / Qwen Team": -2.8,
    "Qwen2.5-Coder 32B InstructAlibaba Cloud / Qwen Team": -3.3,
    "Qwen3.5-2BAlibaba Cloud / Qwen Team": -3.4,
    "Granite 3.3 8B InstructIBM": -3.6,
    "Phi-4-multimodal-instructMicrosoft": -4.2,
    "Llama 3.1 8B InstructMeta": -4.5,
    "Gemini DiffusionGoogle": -5.0,
    "Llama 3.1 Nemotron 70B InstructNVIDIA": -5.2,
    "Grok-1.5xAI": -5.7,
    "Claude 3.5 HaikuAnthropic": -5.8,
    "DeepSeek VL2DeepSeek": -6.0,
    "Command R+Cohere": -6.3,
    "Gemma 2 9BGoogle": -6.8,
    "Ministral 8B InstructMistral AI": -7.1,
    "Grok-1.5VxAI": -7.2,
    "Granite 3.3 8B BaseIBM": -7.3,
    "Phi-3.5-mini-instructMicrosoft": -7.3,
    "Qwen2.5-Omni-7BAlibaba Cloud / Qwen Team": -7.5,
    "Claude 3 HaikuAnthropic": -7.6,
    "Gemma 3 4BGoogle": -8.8,
    "Llama 3.2 3B InstructMeta": -9.1,
    "Qwen2 7B InstructAlibaba Cloud / Qwen Team": -9.5,
    "Phi 4 MiniMicrosoft": -9.6,
    "Mistral NeMo InstructMistral AI": -9.9,
    "Jamba 1.5 MiniAI21 Labs": -9.9,
    "Gemma 3n E4BGoogle": -10.2,
    "Pixtral-12BMistral AI": -11.1,
    "Qwen2.5-Coder 7B InstructAlibaba Cloud / Qwen Team": -11.1,
    "DeepSeek VL2 SmallDeepSeek": -11.5,
    "Llama 3.2 11B InstructMeta": -12.3,
    "Gemma 3n E4B InstructedGoogle": -13.3,
    "IBM Granite 4.0 Tiny PreviewIBM": -14.1,
    "Gemini 1.0 ProGoogle": -14.3,
    "DeepSeek R1 Distill Qwen 1.5BDeepSeek": -14.8,
    "ERNIE 4.5Baidu": -15.8,
    "Phi-3.5-vision-instructMicrosoft": -16.1,
    "GPT-3.5 TurboOpenAI": -16.8,
    "Gemma 3n E2BGoogle": -17.8,
    "Qwen3.5-0.8BAlibaba Cloud / Qwen Team": -17.8,
    "DeepSeek VL2 TinyDeepSeek": -18.9,
    "Gemma 3 1BGoogle": -19.2,
    "Gemma 3n E2B InstructedGoogle": -20.4,
}

PROVIDERS = [
    "Anthropic", "OpenAI", "Google", "Meta", "DeepSeek", "xAI",
    "Moonshot AI", "Zhipu AI", "ByteDance", "Alibaba Cloud / Qwen Team",
    "Alibaba", "MiniMax", "StepFun", "Nous Research", "Cohere",
    "AI21 Labs", "NVIDIA", "Amazon", "Perplexity", "IBM", "Databricks",
    "Mistral AI", "Stability AI", "Reka", "MiMo", "Muse", "LongCat",
    "OpenBMB", "Baidu", "Tencent", "iFlytek", "SenseTime", "Kling",
    "Hunyuan", "HiDream", "LG AI Research", "TII", "Upstage", "Adept",
    "Snowflake", "EleutherAI", "Allen AI", "Xiaomi", "Meituan",
    "Inception", "Sarvam AI", "Microsoft",
]
PROVIDERS.sort(key=len, reverse=True)


def clean_name(raw: str) -> tuple[str, str]:
    """Extract model name and provider from concatenated homepage cell."""
    cleaned = re.sub(r'(UNRELEASED|NEW\d*|UPDATED\d*)', '', raw).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    for prov in PROVIDERS:
        if cleaned.endswith(prov):
            model = cleaned[:-len(prov)].strip()
            return model, prov

    m = re.match(r'^(.+?)\s+([A-Z][A-Za-z /&]+(?:Team|Research|AI)?)$', cleaned)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    return cleaned, ""


def match_model(seed_model: dict, scraped_name: str, scraped_prov: str) -> bool:
    """Check if a seed model matches the scraped model using exact name comparison."""
    sm_name = (seed_model.get("name") or "").strip().lower()
    sm_slug = (seed_model.get("id") or "").strip().lower()
    sm_prov = (
        seed_model.get("provider", {}).get("name")
        or seed_model.get("provider", {}).get("id")
        or ""
    ).strip().lower()

    sn = scraped_name.strip().lower()
    sp = scraped_prov.strip().lower()

    # 1. Exact name match (case insensitive)
    if sm_name == sn:
        return True

    # 2. Slug match: convert homepage name to slug format
    # e.g. "GPT-5.5 Pro" -> "gpt-5.5-pro"
    sn_slug = re.sub(r'[^a-z0-9]+', '-', sn).strip('-')
    if sm_slug == sn_slug:
        return True

    # 3. Seed name equals homepage name with provider suffix removed
    # Sometimes the seed uses a shorter name variant
    if sm_name == sn:
        return True

    return False


def update_seed(models: dict, seed_path: str) -> int:
    # Build lookup by cleaned name only (model names are unique enough)
    lookup: dict[str, float] = {}
    for raw_name, score in models.items():
        name, prov = clean_name(raw_name)
        key = name.strip().lower()
        lookup[key] = score

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = json.load(f)

    updated = 0
    for sm in seed:
        sm_name = (sm.get("name") or "").strip().lower()
        sm_slug = (sm.get("id") or "").strip().lower()

        score = None

        # 1. Exact name match
        if sm_name in lookup:
            score = lookup[sm_name]
        else:
            # 2. Slug match: convert homepage names to slugs
            for sn, s in lookup.items():
                sn_slug = re.sub(r'[^a-z0-9]+', '-', sn).strip('-')
                if sm_slug == sn_slug:
                    score = s
                    break

        if score is not None:
            old = sm.get("overall_score")
            sm["overall_score"] = score
            if old != score:
                updated += 1

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)

    return updated


if __name__ == "__main__":
    seed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    for seed_file in [
        "seed_models.json",
        "seed_image_models.json",
        "seed_video_models.json",
        "seed_tts_models.json",
        "seed_stt_models.json",
    ]:
        path = os.path.join(seed_dir, seed_file)
        if os.path.exists(path):
            n = update_seed(LLM_STATS_DATA, path)
            print(f"Updated {n} models in {seed_file}")

    # Verify top 10
    with open(os.path.join(seed_dir, "seed_models.json"), "r", encoding="utf-8") as f:
        seed = json.load(f)
    sorted_models = sorted(
        [m for m in seed if m.get("overall_score") is not None],
        key=lambda m: m["overall_score"],
        reverse=True,
    )
    print("\nTop 10 after update:")
    for m in sorted_models[:10]:
        print(f"  {m['name']:30s} overall={m['overall_score']}")
