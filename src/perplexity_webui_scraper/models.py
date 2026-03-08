"""AI model definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Model:
    """AI model configuration with metadata."""

    identifier: str
    name: str
    description: str
    tool_name: str
    mode: str = "copilot"
    subscription_tier: str = "pro"


class Models:
    """Available AI models (all use copilot mode with web search)."""

    BEST: ClassVar[Model] = Model(
        identifier="pplx_pro_upgraded",
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
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_sonar",
    )

    GEMINI_3_FLASH: ClassVar[Model] = Model(
        identifier="gemini30flash",
        name="Gemini 3 Flash",
        description="Google's fast model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gemini_flash",
    )

    GEMINI_3_FLASH_THINKING: ClassVar[Model] = Model(
        identifier="gemini30flash_high",
        name="Gemini 3 Flash Thinking",
        description="Google's fast model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gemini_flash_think",
    )

    GEMINI_31_PRO: ClassVar[Model] = Model(
        identifier="gemini31pro_low",
        name="Gemini 3.1 Pro",
        description="Google's latest model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gemini31_pro",
    )

    GEMINI_31_PRO_THINKING: ClassVar[Model] = Model(
        identifier="gemini31pro_high",
        name="Gemini 3.1 Pro Thinking",
        description="Google's latest model with thinking",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gemini31_pro_think",
    )

    GPT_54: ClassVar[Model] = Model(
        identifier="gpt54",
        name="GPT-5.4",
        description="OpenAI's latest model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gpt54",
    )

    GPT_54_THINKING: ClassVar[Model] = Model(
        identifier="gpt54_thinking",
        name="GPT-5.4 Thinking",
        description="OpenAI's latest model with thinking",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_gpt54_thinking",
    )

    CLAUDE_46_SONNET: ClassVar[Model] = Model(
        identifier="claude46sonnet",
        name="Claude Sonnet 4.6",
        description="Anthropic's fast model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_claude_s46",
    )

    CLAUDE_46_SONNET_THINKING: ClassVar[Model] = Model(
        identifier="claude46sonnetthinking",
        name="Claude Sonnet 4.6 Thinking",
        description="Anthropic's newest reasoning model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_claude_s46_think",
    )

    CLAUDE_46_OPUS: ClassVar[Model] = Model(
        identifier="claude46opus",
        name="Claude Opus 4.6",
        description="Anthropic's most advanced model",
        mode="search",
        subscription_tier="max",
        tool_name="pplx_claude_o46",
    )

    CLAUDE_46_OPUS_THINKING: ClassVar[Model] = Model(
        identifier="claude46opusthinking",
        name="Claude Opus 4.6 Thinking",
        description="Anthropic's Opus reasoning model with thinking",
        mode="search",
        subscription_tier="max",
        tool_name="pplx_claude_o46_think",
    )

    GROK_41: ClassVar[Model] = Model(
        identifier="grok41nonreasoning",
        name="Grok 4.1",
        description="xAI's latest model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_grok41",
    )

    GROK_41_THINKING: ClassVar[Model] = Model(
        identifier="grok41reasoning",
        name="Grok 4.1 Thinking",
        description="xAI's latest model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_grok41_think",
    )

    KIMI_K25_THINKING: ClassVar[Model] = Model(
        identifier="kimik25thinking",
        name="Kimi K2.5",
        description="Moonshot AI's latest model",
        mode="search",
        subscription_tier="pro",
        tool_name="pplx_kimi_k25_think",
    )

    @classmethod
    def all(cls) -> list[Model]:
        """Return all available models."""

        return [
            cls.BEST,
            cls.DEEP_RESEARCH,
            cls.SONAR,
            cls.GEMINI_3_FLASH,
            cls.GEMINI_3_FLASH_THINKING,
            cls.GEMINI_31_PRO,
            cls.GEMINI_31_PRO_THINKING,
            cls.GPT_54,
            cls.GPT_54_THINKING,
            cls.CLAUDE_46_SONNET,
            cls.CLAUDE_46_SONNET_THINKING,
            cls.CLAUDE_46_OPUS,
            cls.CLAUDE_46_OPUS_THINKING,
            cls.GROK_41,
            cls.GROK_41_THINKING,
            cls.KIMI_K25_THINKING,
        ]

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
