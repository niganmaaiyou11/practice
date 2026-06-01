from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date


@dataclass
class ParsedUsageData:
    provider: str
    model_name: str | None
    input_tokens: int | None
    output_tokens: int | None
    usage_date: str  # YYYY-MM-DD
    all_models: list[dict] = field(default_factory=list)


class EmailParser:
    provider_name: str = ""
    sender_patterns: list[str] = []
    subject_keywords: list[str] = []

    def parse(self, email: dict) -> ParsedUsageData | None:
        raise NotImplementedError

    @staticmethod
    def _extract_number(text: str, pattern: str) -> int | None:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            num_str = m.group(1).replace(",", "").replace(" ", "").replace("_", "")
            try:
                return int(num_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def _extract_all_numbers(text: str, pattern: str) -> list[int]:
        """Extract all numbers matching pattern."""
        results = []
        for m in re.finditer(pattern, text, re.IGNORECASE):
            num_str = m.group(1).replace(",", "").replace(" ", "").replace("_", "")
            try:
                results.append(int(num_str))
            except ValueError:
                pass
        return results

    # Words that are NOT model names
    _NON_MODEL_WORDS = {
        "tokens", "token", "total", "input", "output",
        "usage", "used", "cost", "price", "billing",
        "invoice", "summary", "report", "monthly", "daily",
        "api", "key", "credit", "balance", "quota",
        "period", "date", "limit", "rate", "tier",
    }

    @staticmethod
    def _is_likely_model(name: str) -> bool:
        """Check if a string looks like a model name (not a generic word)."""
        if not name:
            return False
        name_lower = name.lower().strip()
        if name_lower in EmailParser._NON_MODEL_WORDS:
            return False
        if len(name) < 3:
            return False
        # Must contain at least one letter (not pure numbers/symbols)
        if not any(c.isalpha() for c in name):
            return False
        return True

    @staticmethod
    def _find_model_token_pairs(text: str) -> list[tuple[str, int]]:
        """Find model:token pairs like 'GPT-4o: 1,234,567 tokens' or 'deepseek-chat 123456 tokens'."""
        pairs = []
        # Pattern 1: "ModelName: 1,234 tokens" (single-line only)
        p1 = re.compile(
            r'([\w\-\.\+]+[ \t]*(?:[\w\-\.\+]+[ \t]*){0,3})[ \t]*[:：][ \t]*([\d,]+)[ \t]*(?:tokens?|Token|TK)',
            re.IGNORECASE,
        )
        for m in p1.finditer(text):
            model = m.group(1).strip().rstrip(":：").strip()
            if not EmailParser._is_likely_model(model):
                continue
            num = m.group(2).replace(",", "")
            try:
                pairs.append((model, int(num)))
            except ValueError:
                pass

        # Pattern 2: "1,234,567 tokens" near a model name (distance-based)
        # Find model names first
        model_pattern = re.compile(
            r'\b(gpt-?4[oOmM]?|gpt-?[0-9\.]+[a-z]?|claude[\s\-]?[0-9\.]+[\s\-]?[a-z]*|'
            r'gemini[\s\-]?[0-9\.]+[\s\-]?[a-z]*|deepseek[\s\-]?[a-z0-9\-]+|'
            r'llama[\s\-]?[0-9\.]+[\s\-]?[a-z]*|mixtral[\s\-]?[0-9\.]+[\s\-]?[a-z]*|'
            r'qwen[\s\-]?[0-9\.]+[\s\-]?[a-z]*|doubao[\s\-]?[a-z0-9\-]+|'
            r'ernie[\s\-]?[0-9\.]+[\s\-]?[a-z]*|spark[\s\-]?[a-z0-9\-]+|'
            r'glm[\s\-]?[0-9\.]+[\s\-]?[a-z]*|kimi[\s\-]?[a-z0-9\-]*|'
            r'yi[\s\-]?[0-9\.]+[\s\-]?[a-z]*|moonshot[\s\-]?[a-z0-9\-]*|'
            r'step[\s\-]?[0-9\.]+[\s\-]?[a-z]*|abab[\s\-]?[0-9\.]+[\s\-]?[a-z]*|'
            r'baichuan[\s\-]?[a-z0-9\-]*|minimax[\s\-]?[a-z0-9\-]*|'
            r'gro[kq][\s\-]?[0-9\.]+[\s\-]?[a-z]*|command[\s\-]?[a-z0-9\-]*|'
            r'perplexity[\s\-]?[a-z0-9\-]*|sonar[\s\-]?[a-z0-9\-]*|'
            r'o[0-9]+[\s\-]?[a-z]*|r[0-9]+[\s\-]?[a-z]*)\b',
            re.IGNORECASE,
        )
        token_pattern = re.compile(r'([\d,]+)\s*(?:tokens?|Token|TK|T)', re.IGNORECASE)

        model_matches = [(m.start(), m.end(), m.group(1).strip()) for m in model_pattern.finditer(text)]
        token_matches = [(m.start(), m.end(), m.group(1).replace(",", "")) for m in token_pattern.finditer(text)]

        seen = set(p[0].lower() for p in pairs)
        for t_start, t_end, token_str in token_matches:
            for m_start, m_end, model_name in model_matches:
                if model_name.lower() in seen:
                    continue
                if not EmailParser._is_likely_model(model_name):
                    continue
                # Model must be within 200 chars before or 50 chars after the token number
                if (m_end <= t_start and t_start - m_end < 200) or (t_end <= m_start and m_start - t_end < 50):
                    try:
                        pairs.append((model_name, int(token_str)))
                        seen.add(model_name.lower())
                    except ValueError:
                        pass

        # Pattern 3: Table rows with model name and token count in adjacent columns
        # e.g., | deepseek-chat | 123456 | or deepseek-chat  123456  (whitespace-separated)
        table_pattern = re.compile(
            r'([\w\-\.\+]{3,40})\s{2,}([\d,]{3,20})\s*(?:tokens?)?',
            re.IGNORECASE,
        )
        for m in table_pattern.finditer(text):
            candidate = m.group(1).strip()
            if not EmailParser._is_likely_model(candidate):
                continue
            if candidate.lower() in seen:
                continue
            num = m.group(2).replace(",", "")
            try:
                pairs.append((candidate, int(num)))
                seen.add(candidate.lower())
            except ValueError:
                pass

        return pairs


class OpenAIParser(EmailParser):
    provider_name = "openai"
    sender_patterns = ["@openai.com", "@email.openai.com", "@mail.openai.com"]
    subject_keywords = ["usage", "billing", "invoice", "用量", "账单"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        subject = email.get("subject", "").lower()
        if not any(kw.lower() in subject for kw in self.subject_keywords):
            return None

        total_tokens = self._extract_number(combined, r'Total tokens? used[:\s]*([\d,]+)')
        input_tokens = self._extract_number(combined, r'Input tokens?[:\s]*([\d,]+)')
        output_tokens = self._extract_number(combined, r'Output tokens?[:\s]*([\d,]+)')
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for model_name, tokens in pairs:
            all_models.append({"model_name": model_name, "total_tokens": tokens})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(
                provider="OpenAI",
                model_name=first["model_name"],
                input_tokens=first.get("total_tokens", 0),
                output_tokens=0,
                usage_date=usage_date,
                all_models=all_models,
            )
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(
                provider="OpenAI",
                model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
            )
        return None


class AnthropicParser(EmailParser):
    provider_name = "anthropic"
    sender_patterns = ["@anthropic.com", "@email.anthropic.com", "@mail.anthropic.com"]
    subject_keywords = ["billing", "invoice", "usage", "账单"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        total_tokens = self._extract_number(combined, r'Total tokens?[:\s]*([\d,]+)')
        input_tokens = self._extract_number(combined, r'Input tokens?[:\s]*([\d,]+)')
        output_tokens = self._extract_number(combined, r'Output tokens?[:\s]*([\d,]+)')
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for model_name, tokens in pairs:
            all_models.append({"model_name": model_name, "total_tokens": tokens})

        if total_tokens or input_tokens or output_tokens or all_models:
            return ParsedUsageData(
                provider="Anthropic",
                model_name=all_models[0]["model_name"] if all_models else None,
                input_tokens=input_tokens or (total_tokens or 0),
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
                all_models=all_models,
            )
        return None


class GoogleParser(EmailParser):
    provider_name = "google"
    sender_patterns = ["@google.com", "@cloud.google.com", "@googleapis.com", "@googlemail.com"]
    subject_keywords = ["billing", "usage", "invoice", "AI", "gemini", "vertex"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        total_tokens = self._extract_number(combined, r'Total[:\s]*([\d,]+)\s*tokens?')
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        model_name = None
        m = re.search(r'(Gemini[\s\-\.]?\w+)', combined, re.IGNORECASE)
        if m:
            model_name = m.group(1).strip()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            if not model_name:
                model_name = mn
            all_models.append({"model_name": mn, "total_tokens": tokens})

        if total_tokens or all_models:
            return ParsedUsageData(
                provider="Google",
                model_name=model_name,
                input_tokens=total_tokens or 0,
                output_tokens=0,
                usage_date=usage_date,
                all_models=all_models,
            )
        return None


class DeepSeekParser(EmailParser):
    provider_name = "deepseek"
    sender_patterns = [
        "@deepseek.com", "@deepseek.ai", "@platform.deepseek.com",
        "@mail.deepseek.com", "@email.deepseek.com",
    ]
    subject_keywords = [
        "billing", "usage", "用量", "账单", "token", "消费", "使用",
        "usage report", "daily", "monthly", "platform",
    ]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        # Try multiple patterns for total tokens (Chinese & English)
        total_tokens = (
            self._extract_number(combined, r'(?:总|Total|合计)\s*tokens?[:\s]*([\d,]+)') or
            self._extract_number(combined, r'(?:使用量|消费)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'(?:本月|本月用量|本月使用)[:\s]*([\d,]+)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|已用|已使用)')
        )
        input_tokens = (
            self._extract_number(combined, r'(?:输入|Input|输入量)[:\s]*([\d,]+)\s*(?:tokens?)?') or
            self._extract_number(combined, r'Input\s*tokens?[:\s]*([\d,]+)')
        )
        output_tokens = (
            self._extract_number(combined, r'(?:输出|Output|输出量)[:\s]*([\d,]+)\s*(?:tokens?)?') or
            self._extract_number(combined, r'Output\s*tokens?[:\s]*([\d,]+)')
        )
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for model_name, tokens in pairs:
            all_models.append({"model_name": model_name, "total_tokens": tokens})

        # Try to find model names in common DeepSeek patterns
        if not all_models:
            ds_models = re.findall(
                r'\b(deepseek[\s\-]?[a-z0-9\-]+|deepseek[\s\-]?(?:chat|reasoner|coder|v[0-9]+))\b',
                combined, re.IGNORECASE,
            )
            for m in ds_models:
                # Try to find a token count near this model
                idx = combined.lower().find(m.lower())
                if idx >= 0:
                    nearby = combined[max(0, idx - 50):idx + 200]
                    t = self._extract_number(nearby, r'([\d,]+)\s*(?:tokens?|Token|TK)')
                    if not t:
                        t = self._extract_number(nearby, r'(?:tokens?|Token)[:\s]*([\d,]+)')
                    if t:
                        all_models.append({"model_name": m.strip(), "total_tokens": t})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(
                provider="DeepSeek",
                model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
                all_models=all_models,
            )
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(
                provider="DeepSeek",
                model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
            )
        return None


class XAIParser(EmailParser):
    provider_name = "xai"
    sender_patterns = ["@xai.com", "@mail.xai.com"]
    subject_keywords = ["billing", "usage", "invoice", "账单"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        total_tokens = self._extract_number(combined, r'Total tokens?[:\s]*([\d,]+)')
        input_tokens = self._extract_number(combined, r'Input tokens?[:\s]*([\d,]+)')
        output_tokens = self._extract_number(combined, r'Output tokens?[:\s]*([\d,]+)')
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for m, t in pairs:
            all_models.append({"model_name": m, "total_tokens": t})

        if total_tokens or all_models:
            return ParsedUsageData(
                provider="xAI",
                model_name=all_models[0]["model_name"] if all_models else None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
                all_models=all_models,
            )
        return None


class MistralParser(EmailParser):
    provider_name = "mistral"
    sender_patterns = ["@mistral.ai", "@mail.mistral.ai"]
    subject_keywords = ["billing", "usage", "invoice", "账单"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        total_tokens = self._extract_number(combined, r'Total tokens?[:\s]*([\d,]+)')
        input_tokens = self._extract_number(combined, r'Input tokens?[:\s]*([\d,]+)')
        output_tokens = self._extract_number(combined, r'Output tokens?[:\s]*([\d,]+)')
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for m, t in pairs:
            all_models.append({"model_name": m, "total_tokens": t})

        if total_tokens or all_models:
            return ParsedUsageData(
                provider="Mistral AI",
                model_name=all_models[0]["model_name"] if all_models else None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
                all_models=all_models,
            )
        return None


class ZhipuParser(EmailParser):
    provider_name = "zhipu"
    sender_patterns = ["@zhipuai.cn", "@zhipu.cn", "@bigmodel.cn", "@mail.bigmodel.cn"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'(?:消耗|消费)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)')
        )
        input_tokens = self._extract_number(combined, r'(?:input|输入|输入量)[:\s]*([\d,]+)\s*(?:tokens?)?')
        output_tokens = self._extract_number(combined, r'(?:output|输出|输出量)[:\s]*([\d,]+)\s*(?:tokens?)?')

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        # Also look for GLM model names
        glm_models = re.findall(r'\b(glm[\s\-]?[0-9\.]+[\s\-]?[a-z]*|cogview[\s\-]?[a-z0-9\-]*|cogvideo[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in glm_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="Zhipu AI", model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0, usage_date=usage_date, all_models=all_models)
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(provider="Zhipu AI", model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0, usage_date=usage_date)
        return None


class MoonshotParser(EmailParser):
    provider_name = "moonshot"
    sender_patterns = ["@moonshot.cn", "@moonshot.ai", "@kimi.cn", "@mail.kimi.cn"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)')
        )
        input_tokens = self._extract_number(combined, r'(?:input|输入|输入量)[:\s]*([\d,]+)\s*(?:tokens?)?')
        output_tokens = self._extract_number(combined, r'(?:output|输出|输出量)[:\s]*([\d,]+)\s*(?:tokens?)?')

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        kimi_models = re.findall(r'\b(kimi[\s\-]?[a-z0-9\-]*|moonshot[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in kimi_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="Moonshot AI", model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0, usage_date=usage_date, all_models=all_models)
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(provider="Moonshot AI", model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0, usage_date=usage_date)
        return None


class ByteDanceParser(EmailParser):
    provider_name = "bytedance"
    sender_patterns = ["@bytedance.com", "@volcengine.com", "@mail.volcengine.com"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用", "doubao", "豆包"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)') or
            self._extract_number(combined, r'(?:消费|消耗|使用)[:\s]*([\d,]+)\s*(?:tokens?|Token)')
        )
        input_tokens = self._extract_number(combined, r'(?:input|输入|输入量)[:\s]*([\d,]+)\s*(?:tokens?)?')
        output_tokens = self._extract_number(combined, r'(?:output|输出|输出量)[:\s]*([\d,]+)\s*(?:tokens?)?')

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        doubao_models = re.findall(r'\b(doubao[\s\-]?[a-z0-9\-]*|skylark[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in doubao_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="ByteDance", model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0, usage_date=usage_date, all_models=all_models)
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(provider="ByteDance", model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0, usage_date=usage_date)
        return None


class MiniMaxParser(EmailParser):
    provider_name = "minimax"
    sender_patterns = ["@minimax.com", "@minimaxi.com", "@mail.minimax.com"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)')
        )

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        abab_models = re.findall(r'\b(abab[\s\-]?[0-9\.]+[\s\-]?[a-z]*|minimax[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in abab_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="MiniMax", model_name=first["model_name"],
                input_tokens=first.get("total_tokens", total_tokens or 0),
                output_tokens=0, usage_date=usage_date, all_models=all_models)
        if total_tokens:
            return ParsedUsageData(provider="MiniMax", model_name=None,
                input_tokens=total_tokens, output_tokens=0, usage_date=usage_date)
        return None


class StepFunParser(EmailParser):
    provider_name = "stepfun"
    sender_patterns = ["@stepfun.com", "@mail.stepfun.com"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)')
        )

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        step_models = re.findall(r'\b(step[\s\-]?[0-9\.]+[\s\-]?[a-z]*)', combined, re.IGNORECASE)
        for m in step_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="StepFun", model_name=first["model_name"],
                input_tokens=first.get("total_tokens", total_tokens or 0),
                output_tokens=0, usage_date=usage_date, all_models=all_models)
        if total_tokens:
            return ParsedUsageData(provider="StepFun", model_name=None,
                input_tokens=total_tokens, output_tokens=0, usage_date=usage_date)
        return None


class BaichuanParser(EmailParser):
    provider_name = "baichuan"
    sender_patterns = ["@baichuan.cn", "@baichuan.com", "@mail.baichuan.cn"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)')
        )

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        baichuan_models = re.findall(r'\b(baichuan[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in baichuan_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="Baichuan", model_name=first["model_name"],
                input_tokens=first.get("total_tokens", total_tokens or 0),
                output_tokens=0, usage_date=usage_date, all_models=all_models)
        if total_tokens:
            return ParsedUsageData(provider="Baichuan", model_name=None,
                input_tokens=total_tokens, output_tokens=0, usage_date=usage_date)
        return None


class AlibabaParser(EmailParser):
    provider_name = "alibaba"
    sender_patterns = ["@alibaba-inc.com", "@alibabacloud.com", "@aliyun.com", "@mail.aliyun.com"]
    subject_keywords = ["billing", "usage", "用量", "账单", "消费", "token", "费用", "qwen", "tongyi"]

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合计|使用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|使用|消耗)') or
            self._extract_number(combined, r'(?:消费|消耗|使用)[:\s]*([\d,]+)\s*(?:tokens?|Token)')
        )
        input_tokens = self._extract_number(combined, r'(?:input|输入|输入量)[:\s]*([\d,]+)\s*(?:tokens?)?')
        output_tokens = self._extract_number(combined, r'(?:output|输出|输出量)[:\s]*([\d,]+)\s*(?:tokens?)?')

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for mn, tokens in pairs:
            all_models.append({"model_name": mn, "total_tokens": tokens})
        qwen_models = re.findall(r'\b(qwen[\s\-]?[0-9\.]+[\s\-]?[a-z]*|tongyi[\s\-]?[a-z0-9\-]*)', combined, re.IGNORECASE)
        for m in qwen_models:
            if m not in [am["model_name"] for am in all_models]:
                all_models.append({"model_name": m.strip(), "total_tokens": total_tokens or 0})

        if all_models:
            first = all_models[0]
            return ParsedUsageData(provider="Alibaba", model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0, usage_date=usage_date, all_models=all_models)
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(provider="Alibaba", model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0, usage_date=usage_date)
        return None


class GenericParser(EmailParser):
    """Fallback parser — tries hard to extract any token usage data from unknown senders."""

    provider_name = "generic"
    sender_patterns = []
    subject_keywords = []

    def parse(self, email: dict) -> ParsedUsageData | None:
        text = email.get("body_text", "") or ""
        html = email.get("body_html", "") or ""
        combined = text + "\n" + html

        # Try many patterns for token counts
        total_tokens = (
            self._extract_number(combined, r'(?:total|总|合計|合计)\s*tokens?[:\s]*([\d,]+)') or
            self._extract_number(combined, r'(?:使用量|消费|用量)[:\s]*([\d,]+)\s*(?:tokens?|Token)') or
            self._extract_number(combined, r'Tokens?\s*[：:]\s*([\d,]+)') or
            self._extract_number(combined, r'([\d,]+)\s*tokens?\s*(?:used|consumed|已用|已使用)')
        )
        input_tokens = (
            self._extract_number(combined, r'(?:input|输入|入力)\s*tokens?[:\s]*([\d,]+)') or
            self._extract_number(combined, r'(?:输入量|Input)[:\s]*([\d,]+)')
        )
        output_tokens = (
            self._extract_number(combined, r'(?:output|输出|出力)\s*tokens?[:\s]*([\d,]+)') or
            self._extract_number(combined, r'(?:输出量|Output)[:\s]*([\d,]+)')
        )
        usage_date = email.get("date").strftime("%Y-%m-%d") if email.get("date") else date.today().isoformat()

        all_models = []
        pairs = self._find_model_token_pairs(combined)
        for model_name, tokens in pairs:
            all_models.append({"model_name": model_name, "total_tokens": tokens})

        # Try to determine provider from sender address
        provider = "Unknown"
        from_addr = email.get("from", "").lower()
        provider_domains = {
            "OpenAI": ["openai.com"],
            "Anthropic": ["anthropic.com"],
            "Google": ["google.com", "googleapis.com"],
            "DeepSeek": ["deepseek.com", "deepseek.ai"],
            "xAI": ["xai.com"],
            "Mistral AI": ["mistral.ai"],
            "Cohere": ["cohere.com"],
            "Meta": ["meta.ai"],
            "Perplexity": ["perplexity.ai"],
            "Zhipu AI": ["zhipuai.cn", "zhipu.cn", "bigmodel.cn"],
            "Moonshot AI": ["moonshot.cn", "moonshot.ai", "kimi.cn"],
            "ByteDance": ["bytedance.com", "volcengine.com"],
            "MiniMax": ["minimax.com", "minimaxi.com"],
            "StepFun": ["stepfun.com"],
            "Baichuan": ["baichuan.cn", "baichuan.com"],
            "Alibaba": ["alibaba-inc.com", "alibabacloud.com", "aliyun.com"],
            "iFlytek": ["iflytek.com"],
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
        for p_name, domains in provider_domains.items():
            if any(d in from_addr for d in domains):
                provider = p_name
                break

        if all_models:
            first = all_models[0]
            return ParsedUsageData(
                provider=provider,
                model_name=first["model_name"],
                input_tokens=input_tokens or first.get("total_tokens", 0),
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
                all_models=all_models,
            )
        if total_tokens or input_tokens or output_tokens:
            return ParsedUsageData(
                provider=provider,
                model_name=None,
                input_tokens=input_tokens or total_tokens or 0,
                output_tokens=output_tokens or 0,
                usage_date=usage_date,
            )
        return None


# ── Parser Registry ────────────────────────────────

PARSER_REGISTRY: dict[str, EmailParser] = {}


def register_parser(parser: EmailParser):
    PARSER_REGISTRY[parser.provider_name] = parser


for p in [
    OpenAIParser(), AnthropicParser(), GoogleParser(),
    DeepSeekParser(), XAIParser(), MistralParser(),
    ZhipuParser(), MoonshotParser(), ByteDanceParser(),
    MiniMaxParser(), StepFunParser(), BaichuanParser(),
    AlibabaParser(),
]:
    register_parser(p)


def get_parser_for_sender(from_address: str) -> EmailParser | None:
    """Match sender against registered parser patterns. Falls back to GenericParser."""
    for parser in PARSER_REGISTRY.values():
        for pattern in parser.sender_patterns:
            if pattern.lower() in from_address.lower():
                return parser
    return GenericParser()


def get_parser_by_name(name: str) -> EmailParser | None:
    return PARSER_REGISTRY.get(name)
