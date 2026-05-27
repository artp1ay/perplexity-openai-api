"""AI model definitions and discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
import re
from typing import ClassVar


_JS_STRING_PATTERN = re.compile(r'"((?:[^"\\]|\\.)*)"')
_SCRIPT_SRC_PATTERN = re.compile(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', re.IGNORECASE)
_MODEL_ID_PATTERN = re.compile(
    r'(?:^|[,{])\s*(?:"?(?:identifier|model|model_preference|modelPreference|value|id|code)"?)\s*:\s*"([^"]+)"'
)
_MODEL_KEY_PATTERNS = {
    "name": re.compile(r'(?:^|[,{])\s*"?(?:name|label|title)"?\s*:\s*"([^"]+)"'),
    "description": re.compile(r'(?:^|[,{])\s*"?(?:description|subtitle|tooltip)"?\s*:\s*"([^"]+)"'),
    "mode": re.compile(r'(?:^|[,{])\s*"?(?:mode)"?\s*:\s*"([^"]+)"'),
    "subscription_tier": re.compile(
        r'(?:^|[,{])\s*"?(?:subscription_tier|subscriptionTier|tier|plan)"?\s*:\s*"([^"]+)"'
    ),
}


@dataclass(frozen=True, slots=True)
class Model:
    """AI model configuration with metadata."""

    identifier: str
    name: str
    description: str = ""
    tool_name: str = ""
    mode: str = "copilot"
    subscription_tier: str = "pro"
    source: str = "static"

    def __post_init__(self) -> None:
        if not self.identifier:
            raise ValueError("model identifier cannot be empty")
        if not self.tool_name:
            object.__setattr__(self, "tool_name", Models.tool_name_for(self.identifier))


class Models:
    """Known model registry with dynamic discovery support.

    Class attributes are kept as stable fallbacks for compatibility. Runtime
    callers should prefer :meth:`Perplexity.available_models`, which refreshes
    model metadata from Perplexity's frontend assets and falls back to these
    entries only when discovery is unavailable.
    """

    BEST: ClassVar[Model] = Model(
        identifier="default",
        name="Pro",
        description="Automatically selects the most responsive model based on the query",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_ask",
    )

    DEEP_RESEARCH: ClassVar[Model] = Model(
        identifier="pplx_alpha",
        name="Deep research",
        description="Fast and thorough for routine research",
        mode="research",
        subscription_tier="pro",
        tool_name="pplx_deep_research",
    )

    SONAR: ClassVar[Model] = Model(
        identifier="experimental",
        name="Sonar",
        description="Perplexity's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_sonar",
    )

    GEMINI_3_FLASH: ClassVar[Model] = Model(
        identifier="gemini30flash",
        name="Gemini 3 Flash",
        description="Google's fast model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gemini_flash",
    )

    GEMINI_3_FLASH_THINKING: ClassVar[Model] = Model(
        identifier="gemini30flash_high",
        name="Gemini 3 Flash Thinking",
        description="Google's fast model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gemini_flash_think",
    )

    GEMINI_31_PRO: ClassVar[Model] = Model(
        identifier="gemini31pro_low",
        name="Gemini 3.1 Pro",
        description="Google's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gemini31_pro",
    )

    GEMINI_31_PRO_THINKING: ClassVar[Model] = Model(
        identifier="gemini31pro_high",
        name="Gemini 3.1 Pro Thinking",
        description="Google's latest model with thinking",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gemini31_pro_think",
    )

    GPT_54: ClassVar[Model] = Model(
        identifier="gpt54",
        name="GPT-5.4",
        description="OpenAI's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gpt54",
    )

    GPT_54_THINKING: ClassVar[Model] = Model(
        identifier="gpt54_thinking",
        name="GPT-5.4 Thinking",
        description="OpenAI's latest model with thinking",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_gpt54_thinking",
    )

    CLAUDE_46_SONNET: ClassVar[Model] = Model(
        identifier="claude46sonnet",
        name="Claude Sonnet 4.6",
        description="Anthropic's fast model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_claude_s46",
    )

    CLAUDE_46_SONNET_THINKING: ClassVar[Model] = Model(
        identifier="claude46sonnetthinking",
        name="Claude Sonnet 4.6 Thinking",
        description="Anthropic's newest reasoning model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_claude_s46_think",
    )

    CLAUDE_46_OPUS: ClassVar[Model] = Model(
        identifier="claude46opus",
        name="Claude Opus 4.6",
        description="Anthropic's most advanced model",
        mode="copilot",
        subscription_tier="max",
        tool_name="pplx_claude_o46",
    )

    CLAUDE_46_OPUS_THINKING: ClassVar[Model] = Model(
        identifier="claude46opusthinking",
        name="Claude Opus 4.6 Thinking",
        description="Anthropic's Opus reasoning model with thinking",
        mode="copilot",
        subscription_tier="max",
        tool_name="pplx_claude_o46_think",
    )

    GROK_41: ClassVar[Model] = Model(
        identifier="grok41nonreasoning",
        name="Grok 4.1",
        description="xAI's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_grok41",
    )

    GROK_41_THINKING: ClassVar[Model] = Model(
        identifier="grok41reasoning",
        name="Grok 4.1 Thinking",
        description="xAI's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_grok41_think",
    )

    KIMI_K25_THINKING: ClassVar[Model] = Model(
        identifier="kimik25thinking",
        name="Kimi K2.5",
        description="Moonshot AI's latest model",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_kimi_k25_think",
    )

    LABS: ClassVar[Model] = Model(
        identifier="pplx_beta",
        name="Labs",
        description="Create projects from scratch",
        mode="copilot",
        subscription_tier="pro",
        tool_name="pplx_labs",
    )

    RESEARCH: ClassVar[Model] = DEEP_RESEARCH

    @classmethod
    def all(cls) -> list[Model]:
        """Return bundled fallback models."""

        return [
            value
            for value in vars(cls).values()
            if isinstance(value, Model)
        ]

    @classmethod
    def fallback_map(cls) -> dict[str, Model]:
        """Return bundled models indexed by identifier, name, and tool name."""

        result: dict[str, Model] = {}
        for model in cls.all():
            for key in (model.identifier, model.name, model.tool_name):
                result[key.lower()] = model
        return result

    @classmethod
    def from_identifier(cls, model: str | Model, available_models: list[Model] | None = None) -> Model:
        """Resolve a model object from an OpenAI-style model id or display name."""

        if isinstance(model, Model):
            return model

        model_id = model.strip()
        if not model_id:
            raise ValueError("model cannot be empty")

        candidates = available_models or cls.all()
        lookup: dict[str, Model] = {}
        for candidate in candidates:
            for key in (candidate.identifier, candidate.name, candidate.tool_name):
                lookup[key.lower()] = candidate

        fallback = cls.fallback_map()
        lookup.update({key: value for key, value in fallback.items() if key not in lookup})

        found = lookup.get(model_id.lower())
        if found is not None:
            return found

        return cls.dynamic_model(model_id)

    @classmethod
    def dynamic_model(cls, identifier: str, *, name: str | None = None, mode: str = "copilot") -> Model:
        """Create a model entry for a valid id discovered or provided at runtime."""

        return Model(
            identifier=identifier,
            name=name or _humanize_identifier(identifier),
            description="Runtime model",
            mode=mode,
            subscription_tier="unknown",
            tool_name=cls.tool_name_for(identifier),
            source="runtime",
        )

    @staticmethod
    def tool_name_for(identifier: str) -> str:
        """Return a stable MCP-safe tool name for a model id."""

        slug = re.sub(r"[^a-z0-9]+", "_", identifier.lower()).strip("_")
        return f"pplx_{slug or 'model'}"

    @classmethod
    def merge_discovered(cls, discovered: list[Model]) -> list[Model]:
        """Merge discovered model metadata with fallback metadata."""

        by_id = {model.identifier: model for model in cls.all()}
        for model in discovered:
            fallback = by_id.get(model.identifier)
            if fallback is not None:
                by_id[model.identifier] = replace(
                    fallback,
                    name=model.name or fallback.name,
                    description=model.description or fallback.description,
                    mode=model.mode or fallback.mode,
                    subscription_tier=model.subscription_tier or fallback.subscription_tier,
                    source=model.source,
                )
            else:
                by_id[model.identifier] = model

        return sorted(by_id.values(), key=lambda item: (item.mode != "search", item.name.lower()))

    @classmethod
    def generate_markdown_table(cls) -> str:
        """Generate markdown table for README."""

        lines = [
            "| Model | Description | Tier |",
            "| ----- | ----------- | ---- |",
        ]

        for model in cls.all():
            attr_name = next(
                (name for name, val in vars(cls).items() if val is model),
                model.tool_name.upper(),
            )
            lines.append(f"| `Models.{attr_name}` | {model.name} - {model.description} | {model.subscription_tier} |")

        return "\n".join(lines)


def extract_script_sources(html: str) -> list[str]:
    """Extract JavaScript asset URLs from a Perplexity HTML page."""

    return list(dict.fromkeys(_unescape_js_string(match) for match in _SCRIPT_SRC_PATTERN.findall(html)))


def extract_models_from_text(text: str, *, source: str = "frontend") -> list[Model]:
    """Extract model metadata from frontend HTML or JavaScript text.

    Perplexity does not expose a documented model-list endpoint for the WebUI.
    The frontend bundle is the source of truth for selectable model ids, so this
    parser intentionally accepts several common minified-object shapes instead
    of relying on one brittle hardcoded object path.
    """

    models: dict[str, Model] = {}
    for match in _MODEL_ID_PATTERN.finditer(text):
        identifier = _unescape_js_string(match.group(1))
        if not _looks_like_model_id(identifier):
            continue

        start = max(0, match.start() - 600)
        end = min(len(text), match.end() + 1000)
        window = text[start:end]

        name = _extract_field(window, "name") or _humanize_identifier(identifier)
        description = _extract_field(window, "description")
        mode = _extract_field(window, "mode") or _infer_mode(identifier)
        tier = _extract_field(window, "subscription_tier") or "unknown"

        existing = models.get(identifier)
        if existing is None or (existing.description == "" and description):
            models[identifier] = Model(
                identifier=identifier,
                name=name,
                description=description,
                mode=mode,
                subscription_tier=tier,
                source=source,
            )

    return list(models.values())


def _extract_field(text: str, field: str) -> str:
    pattern = _MODEL_KEY_PATTERNS[field]
    match = pattern.search(text)
    return _unescape_js_string(match.group(1)) if match else ""


def _looks_like_model_id(value: str) -> bool:
    if not value or len(value) > 80 or "/" in value or "." in value:
        return False
    lower = value.lower()
    if lower in {"web", "all", "default", "experimental", "pplx_alpha"}:
        return True
    return any(
        token in lower
        for token in (
            "claude",
            "gemini",
            "gpt",
            "grok",
            "kimi",
            "llama",
            "mistral",
            "o3",
            "o4",
            "opus",
            "sonar",
        )
    )


def _infer_mode(identifier: str) -> str:
    if identifier == "default":
        return "search"
    if identifier == "pplx_alpha":
        return "research"
    return "copilot"


def _humanize_identifier(identifier: str) -> str:
    fallback = identifier.replace("_", " ").replace("-", " ").strip()
    return fallback.title() if fallback else identifier


def _unescape_js_string(value: str) -> str:
    if "\\" not in value:
        return value

    quoted = f'"{value}"'
    match = _JS_STRING_PATTERN.fullmatch(quoted)
    if not match:
        return value

    try:
        return bytes(value, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return value
