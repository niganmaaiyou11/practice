"""
Build seed data JSON files for all 5 modalities.
Run this after updating the raw_data dicts below with fresh scrapes from llm-stats.com.

Usage: (cd backend && python scripts/build_seed_data.py)
"""
from __future__ import annotations
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# ── Provider mapping by slug prefix or model name patterns ──
def guess_provider(slug: str, name: str) -> tuple[str, str]:
    """Return (provider_name, organization_name) based on slug/name heuristics."""
    s = slug.lower()
    n = name.lower()

    if any(x in s for x in ["gpt-image", "dall", "tts-1", "whisper", "openai"]):
        return ("OpenAI", "OpenAI")
    if any(x in s for x in ["gemini", "veo", "imagen", "chirp", "google"]):
        return ("Google", "Google")
    if any(x in s for x in ["claude"]):
        return ("Anthropic", "Anthropic")
    if any(x in s for x in ["flux", "flx", "bfl", "black-forest"]):
        return ("Black Forest Labs", "Black Forest Labs")
    if any(x in s for x in ["seedream", "seedance"]):
        return ("ByteDance", "ByteDance")
    if any(x in s for x in ["kling", "krea"]):
        return ("Kuaishou", "Kuaishou")
    if any(x in s for x in ["hunyuan", "hunyuan"]):
        return ("Tencent", "Tencent")
    if any(x in s for x in ["qwen"]):
        return ("Alibaba", "Alibaba")
    if any(x in s for x in ["recraft"]):
        return ("Recraft", "Recraft")
    if any(x in s for x in ["sora"]):
        return ("OpenAI", "OpenAI")
    if any(x in s for x in ["stable-diffusion", "sd3", "sd-"]):
        return ("Stability AI", "Stability AI")
    if any(x in s for x in ["grok-imagine", "grok"]):
        return ("xAI", "xAI")
    if any(x in s for x in ["reve"]):
        return ("Reve", "Reve")
    if any(x in s for x in ["hailuo", "minimax"]):
        return ("MiniMax", "MiniMax")
    if any(x in s for x in ["riverflow"]):
        return ("Riverflow", "Riverflow")
    if any(x in s for x in ["glm", "cogview", "zhipu"]):
        return ("Zhipu AI", "Zhipu AI")
    if any(x in s for x in ["bagel"]):
        return ("Bagel", "Bagel")
    if any(x in s for x in ["z-image"]):
        return ("Z Image", "Z Image")
    if any(x in s for x in ["sonic", "cartesia"]):
        return ("Cartesia", "Cartesia")
    if any(x in s for x in ["aura"]):
        return ("Aura", "Aura")
    if any(x in s for x in ["eleven"]):
        return ("ElevenLabs", "ElevenLabs")
    if any(x in s for x in ["speech-", "speech02", "speech-02", "speech-2"]):
        return ("OpenAI", "OpenAI")
    if any(x in s for x in ["playai", "play-ai"]):
        return ("PlayAI", "PlayAI")
    if any(x in s for x in ["inworld"]):
        return ("Inworld", "Inworld")
    if any(x in s for x in ["arcana"]):
        return ("Arcana", "Arcana")
    if any(x in s for x in ["nova-", "deepgram"]):
        return ("Deepgram", "Deepgram")
    if any(x in s for x in ["best", "nano", "universal"]):
        return ("Deepgram", "Deepgram")
    if any(x in s for x in ["ink-whisper"]):
        return ("Ink", "Ink")
    if any(x in s for x in ["whisper"]):
        return ("OpenAI", "OpenAI")
    if any(x in s for x in ["voxtral", "mistral"]):
        return ("Mistral", "Mistral")
    if any(x in s for x in ["mochi"]):
        return ("Genmo", "Genmo")
    if any(x in s for x in ["wan-", "wan2", "wan-v"]):
        return ("Alibaba", "Alibaba")
    if any(x in s for x in ["ltx-", "ltx2"]):
        return ("Lightricks", "Lightricks")
    if any(x in s for x in ["t2v-01"]):
        return ("MiniMax", "MiniMax")
    if any(x in s for x in ["happyhorse"]):
        return ("Happy Horse", "Happy Horse")

    return ("Unknown", "Unknown")


def parse_price(val: str) -> float | None:
    """Parse '$0.0530' or '$10.000' → float."""
    if not val or val in ("—", ""):
        return None
    try:
        return float(val.replace("$", "").replace(",", ""))
    except ValueError:
        return None


def parse_latency(val: str) -> float | None:
    """Parse '81.96s' or '2405ms' → float (seconds)."""
    if not val or val in ("—", ""):
        return None
    try:
        if val.endswith("ms"):
            return float(val[:-2]) / 1000
        if val.endswith("s"):
            return float(val[:-1])
        return float(val)
    except ValueError:
        return None


def parse_speed(val: str) -> float | None:
    """Parse '0.7/min' or '24c/s' → float (per-second)."""
    if not val or val in ("—", ""):
        return None
    try:
        if "/min" in val:
            return float(val.split("/")[0]) / 60
        if "c/s" in val:
            return float(val.replace("c/s", ""))
        if "/s" in val:
            return float(val.split("/")[0])
        return float(val)
    except ValueError:
        return None


# ── Raw scraped data ──
# Re-paste fresh scrapes from puppeteer here when updating.

IMAGE_MODELS_RAW = [
    {"slug":"gpt-image-2","name":"GPT Image 2","resolution":"2K","price":"$0.0530","speed":"0.7/min","latency":"81.96s","arena":"2,904"},
    {"slug":"gemini-3-pro-image-preview","name":"Gemini 3 Pro Image","resolution":"2K","price":"$0.1300","speed":"0.2/min","latency":"46.92s","arena":"2,652"},
    {"slug":"seedream-4.5","name":"Seedream 4.5","resolution":"2K","price":"$0.0400","speed":"0.7/min","latency":"48.54s","arena":"2,646"},
    {"slug":"gpt-image-1.5","name":"GPT Image 1.5","resolution":"2K","price":"$0.0500","speed":"1.1/min","latency":"49.97s","arena":"2,592"},
    {"slug":"hunyuan-image-3","name":"Hunyuan Image 3","resolution":"2K","price":"$0.0900","speed":"1.0/min","latency":"65.85s","arena":"2,575"},
    {"slug":"gemini-2.5-flash-image","name":"Gemini 2.5 Flash Image (Nano Banana)","resolution":"2K","price":"$0.0400","speed":"0.6/min","latency":"30.98s","arena":"2,574"},
    {"slug":"gemini-3.1-flash-image-preview","name":"Gemini 3.1 Flash Image","resolution":"2K","price":"$0.0200","speed":"0.3/min","latency":"44.77s","arena":"2,541"},
    {"slug":"kling-v3-omni-image","name":"Kling v3 Omni Image","resolution":"2K","price":"$0.0280","speed":"1.1/min","latency":"54.07s","arena":"2,523"},
    {"slug":"grok-imagine-image","name":"Grok Imagine Image","resolution":"2K","price":"$0.0200","speed":"6.5/min","latency":"11.98s","arena":"2,520"},
    {"slug":"reve","name":"Reve","resolution":"2K","price":"$0.1800","speed":"3.9/min","latency":"18.74s","arena":"2,438"},
    {"slug":"seedream-4","name":"Seedream 4","resolution":"4K","price":"$0.0300","speed":"1.8/min","latency":"35.00s","arena":"2,406"},
    {"slug":"flux-2-pro","name":"Flux 2 Pro","resolution":"4K","price":"$0.0200","speed":"1.9/min","latency":"25.65s","arena":"2,386"},
    {"slug":"flux-2-max","name":"Flux 2 Max","resolution":"2K","price":"$0.0700","speed":"1.0/min","latency":"50.51s","arena":"2,383"},
    {"slug":"flux-kontext-pro","name":"Flux Kontext Pro","resolution":"4K","price":"$0.0400","speed":"2.1/min","latency":"27.49s","arena":"2,285"},
    {"slug":"flux-2-flex","name":"Flux 2 Flex","resolution":"2K","price":"$0.0500","speed":"1.9/min","latency":"26.80s","arena":"2,261"},
    {"slug":"gpt-image-1","name":"GPT Image 1","resolution":"2K","price":"$0.0400","speed":"1.1/min","latency":"51.51s","arena":"2,139"},
    {"slug":"qwen-image-edit","name":"Qwen Image Edit","resolution":"4K","price":"$0.0300","speed":"3.4/min","latency":"17.92s","arena":"2,129"},
    {"slug":"flux-kontext-max","name":"Flux Kontext Max","resolution":"4K","price":"$0.0800","speed":"1.5/min","latency":"37.32s","arena":"2,065"},
    {"slug":"gpt-image-1-mini","name":"GPT Image 1 Mini","resolution":"2K","price":"$0.0100","speed":"1.3/min","latency":"47.66s","arena":"1,964"},
    {"slug":"flux-1.1-pro","name":"Flux 1.1 Pro","resolution":"4K","price":"$0.0400","speed":"4.9/min","latency":"12.25s","arena":"1,883"},
    {"slug":"riverflow-2.0-pro","name":"Riverflow 2.0 Pro","resolution":"4K","price":"$0.1500","speed":"0.6/min","latency":"99.12s","arena":"1,656"},
    {"slug":"flux-1.1-pro-ultra","name":"Flux 1.1 Pro Ultra","resolution":"4K","price":"$0.0600","speed":"1.9/min","latency":"30.43s","arena":"1,623"},
    {"slug":"riverflow-2.0-fast","name":"Riverflow 2.0 Fast","resolution":"4K","price":"$0.0400","speed":"0.9/min","latency":"73.33s","arena":"1,508"},
    {"slug":"flux-2-klein","name":"Flux 2 Klein","resolution":"4K","price":"$0.0200","speed":"9.2/min","latency":"9.99s","arena":"1,414"},
    {"slug":"flux-2-dev-turbo","name":"Flux 2 Dev Turbo","resolution":"2K","price":"$0.0080","speed":"7.0/min","latency":"12.24s","arena":"-120"},
    {"slug":"qwen-image-2.0","name":"Qwen Image 2.0","resolution":"2K","price":"$0.0350","speed":"3.1/min","latency":"653.06s","arena":"-185"},
    {"slug":"stable-diffusion-3.5-large","name":"Stable Diffusion 3.5 Large","resolution":"2K","price":"$0.0650","speed":"1.0/min","latency":"89.42s","arena":"-187"},
    {"slug":"qwen-image","name":"Qwen Image","resolution":"4K","price":"$0.0300","speed":"4.8/min","latency":"14.31s","arena":"-284"},
    {"slug":"seedream-3","name":"Seedream 3","resolution":"4K","price":"$0.0300","speed":"2.5/min","latency":"10.75s","arena":"-292"},
    {"slug":"flux-2-dev","name":"Flux 2 Dev","resolution":"2K","price":"$0.0120","speed":"6.6/min","latency":"21.41s","arena":"-293"},
    {"slug":"glm-image","name":"GLM Image","resolution":"2K","price":"$0.0500","speed":"0.1/min","latency":"71.21s","arena":"-303"},
    {"slug":"recraft-v3","name":"Recraft V3","resolution":"4K","price":"$0.0400","speed":"4.2/min","latency":"16.66s","arena":"-309"},
    {"slug":"qwen-image-2512","name":"Qwen Image 2512","resolution":"2K","price":"$0.0200","speed":"2.1/min","latency":"37.15s","arena":"-338"},
    {"slug":"cogView-4-250304","name":"CogView 4","resolution":"2K","price":"$0.0300","speed":"0.6/min","latency":"17.86s","arena":"-459"},
    {"slug":"z-image-turbo","name":"Z Image Turbo","resolution":"2K","price":"$0.0050","speed":"7.5/min","latency":"8.99s","arena":"-607"},
    {"slug":"bagel","name":"Bagel","resolution":"2K","price":"$0.1000","speed":"0.4/min","latency":"126.20s","arena":"-912"},
]

VIDEO_MODELS_RAW = [
    {"slug":"grok-imagine-video","name":"Grok Imagine Video","price":"$0.05/s","speed":"2.9s/m","latency":"27.92s","arena":"2,593"},
    {"slug":"kling-v2.5-turbo-pro","name":"Kling v2.5 Turbo Pro","price":"$0.07/s","speed":"1.2s/m","latency":"135.72s","arena":"2,591"},
    {"slug":"veo-3.1-generate-preview","name":"Veo 3.1","price":"$0.40/s","speed":"0.3s/m","latency":"53.55s","arena":"2,521"},
    {"slug":"kling-v2.6","name":"Kling v2.6 Pro","price":"$0.07/s","speed":"0.8s/m","latency":"149.78s","arena":"2,495"},
    {"slug":"veo-3.0-fast-generate-001","name":"Veo 3.0 Fast","price":"$0.15/s","speed":"0.3s/m","latency":"43.05s","arena":"2,486"},
    {"slug":"veo-3.1-fast-generate-preview","name":"Veo 3.1 Fast","price":"$0.15/s","speed":"0.6s/m","latency":"61.45s","arena":"2,483"},
    {"slug":"veo-3.0-generate-001","name":"Veo 3.0","price":"$0.40/s","speed":"0.4s/m","latency":"143.45s","arena":"2,450"},
    {"slug":"wan-2.6-i2v","name":"WAN Video 2.6 I2V","price":"$0.10/s","speed":"0.1s/m","latency":"52.68s","arena":"2,374"},
    {"slug":"seedance-1.5-pro","name":"Seedance 1.5 Pro","price":"$0.10/s","speed":"0.1s/m","latency":"88.73s","arena":"2,365"},
    {"slug":"wan-2.5-i2v","name":"WAN Video 2.5 Image-to-Video","price":"$0.05/s","speed":"3.0s/m","latency":"81.77s","arena":"2,362"},
    {"slug":"seedance-1-pro","name":"SeeDance 1 Pro","price":"$0.06/s","speed":"1.3s/m","latency":"62.42s","arena":"2,343"},
    {"slug":"hailuo-02","name":"Hailuo 02","price":"$0.08/s","speed":"1.4s/m","latency":"81.71s","arena":"2,310"},
    {"slug":"kling-v2.1-master","name":"Kling v2.1 Master","price":"$0.07/s","speed":"1.0s/m","latency":"213.27s","arena":"2,291"},
    {"slug":"hailuo-2.3","name":"Hailuo 2.3","price":"$0.10/s","speed":"2.5s/m","latency":"98.97s","arena":"2,280"},
    {"slug":"seedance-1-lite","name":"SeeDance 1 Lite","price":"$0.04/s","speed":"3.8s/m","latency":"71.61s","arena":"2,240"},
    {"slug":"sora-2","name":"Sora 2","price":"$0.10/s","speed":"1.8s/m","latency":"97.41s","arena":"2,223"},
    {"slug":"seedance-1-pro-fast","name":"SeeDance 1 Pro Fast","price":"$0.03/s","speed":"1.2s/m","latency":"35.33s","arena":"2,166"},
    {"slug":"ltx-2.3-fast","name":"LTX-2.3 Fast","price":"$0.04/s","speed":"8.7s/m","latency":"41.81s","arena":"2,022"},
    {"slug":"ltx-2-19b","name":"LTX-2 19B","price":"$0.04/s","speed":"1.0s/m","latency":"42.88s","arena":"1,993"},
    {"slug":"sora-2-pro","name":"Sora 2 Pro","price":"$0.30/s","speed":"1.1s/m","latency":"168.01s","arena":"1,988"},
    {"slug":"veo-2.0-generate-001","name":"Veo 2.0","price":"$0.30/s","speed":"—","latency":"—","arena":"1,836"},
    {"slug":"wan-2.1-14b","name":"Wan 2.1 14B","price":"$0.08/s","speed":"0.8s/m","latency":"185.21s","arena":"1,577"},
    {"slug":"t2v-01-director","name":"T2V-01-Director","price":"$0.00/s","speed":"1.6s/m","latency":"179.26s","arena":"1,547"},
    {"slug":"hunyuan-video","name":"Hunyuan Video","price":"$0.08/s","speed":"0.1s/m","latency":"747.22s","arena":"1,155"},
    {"slug":"wan-2.6-t2v","name":"WAN Video 2.6","price":"$0.10/s","speed":"1.4s/m","latency":"69.76s","arena":"577"},
    {"slug":"hunyuan-video-1.5","name":"HunyuanVideo 1.5","price":"$0.07/s","speed":"—","latency":"—","arena":"568"},
    {"slug":"kling-v3-omni-video","name":"Kling v3 Omni Video","price":"$0.11/s","speed":"2.2s/m","latency":"110.07s","arena":"-125"},
    {"slug":"happyhorse-1.0","name":"Happy Horse 1.0","price":"$0.14/s","speed":"1.1s/m","latency":"86.17s","arena":""},
    {"slug":"kling-v3","name":"Kling v3","price":"$0.17/s","speed":"2.5s/m","latency":"93.34s","arena":""},
    {"slug":"krea-realtime","name":"Krea Realtime","price":"$0.03/s","speed":"0.6s/m","latency":"239.57s","arena":""},
    {"slug":"ltx-2.3-pro","name":"LTX-2.3 Pro","price":"$0.08/s","speed":"4.0s/m","latency":"70.89s","arena":""},
    {"slug":"ltx-2-fast","name":"LTX-2 Fast","price":"$0.04/s","speed":"—","latency":"—","arena":""},
    {"slug":"ltx-2-pro","name":"LTX-2 Pro","price":"$0.06/s","speed":"—","latency":"—","arena":""},
    {"slug":"mochi-1","name":"Mochi 1","price":"$0.08/s","speed":"0.1s/m","latency":"671.18s","arena":""},
    {"slug":"seedance-2.0-fast","name":"Seedance 2.0 Fast","price":"$0.24/s","speed":"1.9s/m","latency":"118.18s","arena":""},
    {"slug":"seedance-2.0-pro","name":"Seedance 2.0 Pro","price":"$0.30/s","speed":"1.1s/m","latency":"184.60s","arena":""},
    {"slug":"wan-2.2-a14b","name":"Wan 2.2 A14B","price":"$0.08/s","speed":"0.4s/m","latency":"312.52s","arena":""},
    {"slug":"wan-v2.7","name":"WAN 2.7","price":"$0.10/s","speed":"0.6s/m","latency":"66.05s","arena":""},
]

TTS_MODELS_RAW = [
    {"slug":"sonic-3","name":"Sonic 3","price":"$10.000","speed":"24c/s","latency":"2405ms"},
    {"slug":"sonic-english","name":"Sonic English","price":"$10.000","speed":"6c/s","latency":"1692ms"},
    {"slug":"sonic-multilingual","name":"Sonic Multilingual","price":"$15.000","speed":"42c/s","latency":"2805ms"},
    {"slug":"aura-asteria-en","name":"Aura Asteria","price":"$15.000","speed":"819c/s","latency":"912ms"},
    {"slug":"aura-luna-en","name":"Aura Luna","price":"$15.000","speed":"32c/s","latency":"350ms"},
    {"slug":"aura-stella-en","name":"Aura Stella","price":"$15.000","speed":"161c/s","latency":"1797ms"},
    {"slug":"eleven_flash_v2_5","name":"Eleven Flash v2.5","price":"$5.000","speed":"25c/s","latency":"658ms"},
    {"slug":"eleven_turbo_v2_5","name":"Eleven Turbo v2.5","price":"$10.000","speed":"—","latency":"—"},
    {"slug":"eleven_v3","name":"Eleven v3","price":"$30.000","speed":"14c/s","latency":"2990ms"},
    {"slug":"eleven_multilingual_v2","name":"Multilingual V2","price":"$15.000","speed":"70c/s","latency":"3529ms"},
    {"slug":"eleven_turbo_v2","name":"Turbo V2","price":"$5.000","speed":"8c/s","latency":"335ms"},
    {"slug":"speech-02-hd","name":"Speech 02 HD","price":"$15.000","speed":"7c/s","latency":"1832ms"},
    {"slug":"speech-02-turbo","name":"Speech 02 Turbo","price":"$7.500","speed":"—","latency":"—"},
    {"slug":"speech-2.5-hd-preview","name":"Speech 2.5 HD Preview","price":"$20.000","speed":"—","latency":"—"},
    {"slug":"speech-2.5-turbo-preview","name":"Speech 2.5 Turbo Preview","price":"$10.000","speed":"21c/s","latency":"1775ms"},
    {"slug":"tts-1","name":"TTS-1","price":"$15.000","speed":"—","latency":"—"},
    {"slug":"tts-1-hd","name":"TTS-1 HD","price":"$30.000","speed":"—","latency":"—"},
    {"slug":"playai-tts","name":"PlayAI Dialog v1.0","price":"$50.000","speed":"—","latency":"—"},
    {"slug":"inworld-tts-1","name":"Inworld TTS-1","price":"$0.000","speed":"—","latency":"—"},
    {"slug":"inworld-tts-1-max","name":"Inworld TTS-1-Max","price":"$0.000","speed":"—","latency":"—"},
    {"slug":"arcana","name":"Arcana V2","price":"$40.000","speed":"31c/s","latency":"5165ms"},
    # Some video models also appear on TTS page (they have TTS capability) — skip those
]

STT_MODELS_RAW = [
    {"slug":"best","name":"Best","price":"$0.0090","speed":"—","latency":"—"},
    {"slug":"nano","name":"Nano","price":"$0.0090","speed":"—","latency":"—"},
    {"slug":"universal-streaming","name":"Universal Streaming","price":"$0.0090","speed":"—","latency":"—"},
    {"slug":"ink-whisper","name":"Ink-Whisper","price":"$0.0022","speed":"—","latency":"—"},
    {"slug":"nova-2","name":"Nova 2","price":"$0.0070","speed":"—","latency":"—"},
    {"slug":"nova-2-medical","name":"Nova 2 Medical","price":"$0.0070","speed":"—","latency":"—"},
    {"slug":"nova-3","name":"Nova 3","price":"$0.0070","speed":"—","latency":"—"},
    {"slug":"whisper-v3-large","name":"Whisper V3 Large","price":"$0.0018","speed":"—","latency":"—"},
    {"slug":"whisper-v3-turbo","name":"Whisper V3 Turbo","price":"$0.0007","speed":"—","latency":"—"},
    {"slug":"whisper-large-v3","name":"Whisper Large V3","price":"$0.0018","speed":"—","latency":"—"},
    {"slug":"whisper-large-v3-turbo","name":"Whisper Large V3 Turbo","price":"$0.0007","speed":"—","latency":"—"},
    {"slug":"voxtral-mini","name":"Voxtral Mini","price":"$0.0670","speed":"—","latency":"—"},
    {"slug":"whisper-1","name":"Whisper V1","price":"$0.0000","speed":"—","latency":"—"},
]


def build_models(raw_list: list[dict], category: str, has_arena: bool = False, has_resolution: bool = False) -> list[dict]:
    """Convert raw scraped data to seed model format."""
    result = []
    for r in raw_list:
        provider, org = guess_provider(r["slug"], r["name"])
        arena_val = r.get("arena", "").replace(",", "")
        arena_rating = float(arena_val) if arena_val and arena_val not in ("", "—") else None

        model = {
            "id": r["slug"],
            "name": r["name"],
            "provider": {"id": provider.lower(), "name": provider},
            "category": category,
            "overall_score": arena_rating,  # Use arena as the primary score where available
            "pricing": {},
            "modalities": [category],
        }

        price = parse_price(r.get("price", ""))
        if price is not None:
            model["pricing"]["input"] = price
            model["price_input"] = price

        if has_resolution:
            model["output_resolution"] = r.get("resolution", "")

        if has_arena and arena_rating is not None:
            model["arena_rating"] = arena_rating

        latency = parse_latency(r.get("latency", ""))
        if latency is not None:
            model["latency"] = latency

        speed = parse_speed(r.get("speed", ""))
        if speed is not None:
            model["tokens_per_second"] = speed  # Reuse field for speed metric

        result.append(model)
    return result


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    categories = [
        ("seed_image_models.json", IMAGE_MODELS_RAW, "image", True, True),
        ("seed_video_models.json", VIDEO_MODELS_RAW, "video", True, False),
        ("seed_tts_models.json", TTS_MODELS_RAW, "tts", False, False),
        ("seed_stt_models.json", STT_MODELS_RAW, "stt", False, False),
    ]

    for filename, raw, cat, has_arena, has_res in categories:
        models = build_models(raw, cat, has_arena, has_res)
        path = os.path.join(DATA_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        print(f"Wrote {len(models)} models to {filename}")


if __name__ == "__main__":
    main()
