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


class Models:
    """Available AI models (all use copilot mode with web search)."""

    DEEP_RESEARCH: ClassVar[Model] = Model(
        identifier="pplx_alpha",
        name="Deep Research",
        description="Create in-depth reports with more sources, charts, and advanced reasoning.",
        tool_name="pplx_deep_research",
    )

    CREATE_FILES_AND_APPS: ClassVar[Model] = Model(
        identifier="pplx_beta",
        name="Create Files and Apps",
        description="Turn your ideas into docs, slides, dashboards, and more (previously Labs).",
        tool_name="pplx_create_files",
    )

    BEST: ClassVar[Model] = Model(
        identifier="pplx_pro",
        name="Best",
        description="Automatically selects the best model based on the query.",
        tool_name="pplx_ask",
    )

    SONAR: ClassVar[Model] = Model(
        identifier="experimental",
        name="Sonar",
        description="Perplexity's latest model.",
        tool_name="pplx_sonar",
    )

    GEMINI_3_FLASH: ClassVar[Model] = Model(
        identifier="gemini30flash",
        name="Gemini 3 Flash",
        description="Google's fast model.",
        tool_name="pplx_gemini_flash",
    )

    GEMINI_3_FLASH_THINKING: ClassVar[Model] = Model(
        identifier="gemini30flash_high",
        name="Gemini 3 Flash Thinking",
        description="Google's fast model with extended thinking.",
        tool_name="pplx_gemini_flash_think",
    )

    GEMINI_3_PRO_THINKING: ClassVar[Model] = Model(
        identifier="gemini30pro",
        name="Gemini 3 Pro Thinking",
        description="Google's most advanced model with extended thinking.",
        tool_name="pplx_gemini_pro_think",
    )

    GPT_52: ClassVar[Model] = Model(
        identifier="gpt52",
        name="GPT-5.2",
        description="OpenAI's latest model.",
        tool_name="pplx_gpt52",
    )

    GPT_52_THINKING: ClassVar[Model] = Model(
        identifier="gpt52_thinking",
        name="GPT-5.2 Thinking",
        description="OpenAI's latest model with extended thinking.",
        tool_name="pplx_gpt52_thinking",
    )

    CLAUDE_45_SONNET: ClassVar[Model] = Model(
        identifier="claude45sonnet",
        name="Claude Sonnet 4.5",
        description="Anthropic's fast model.",
        tool_name="pplx_claude_sonnet",
    )

    CLAUDE_45_SONNET_THINKING: ClassVar[Model] = Model(
        identifier="claude45sonnetthinking",
        name="Claude Sonnet 4.5 Thinking",
        description="Anthropic's fast model with extended thinking.",
        tool_name="pplx_claude_sonnet_think",
    )

    CLAUDE_46_OPUS: ClassVar[Model] = Model(
        identifier="claude46opus",
        name="Claude Opus 4.6",
        description="Anthropic's Opus reasoning model.",
        tool_name="pplx_claude_opus",
    )

    CLAUDE_46_OPUS_THINKING: ClassVar[Model] = Model(
        identifier="claude46opusthinking",
        name="Claude Opus 4.6 Thinking",
        description="Anthropic's Opus reasoning model with extended thinking.",
        tool_name="pplx_claude_opus_think",
    )

    GROK_41: ClassVar[Model] = Model(
        identifier="grok41nonreasoning",
        name="Grok 4.1",
        description="xAI's latest model.",
        tool_name="pplx_grok",
    )

    GROK_41_THINKING: ClassVar[Model] = Model(
        identifier="grok41reasoning",
        name="Grok 4.1 Thinking",
        description="xAI's latest model with extended thinking.",
        tool_name="pplx_grok_thinking",
    )

    KIMI_K25_THINKING: ClassVar[Model] = Model(
        identifier="kimik25thinking",
        name="Kimi K2.5 Thinking",
        description="Moonshot AI's latest model.",
        tool_name="pplx_kimi_thinking",
    )

    @classmethod
    def all(cls) -> list[Model]:
        """Return all available models."""

        return [
            cls.BEST,
            cls.DEEP_RESEARCH,
            cls.CREATE_FILES_AND_APPS,
            cls.SONAR,
            cls.GEMINI_3_FLASH,
            cls.GEMINI_3_FLASH_THINKING,
            cls.GEMINI_3_PRO_THINKING,
            cls.GPT_52,
            cls.GPT_52_THINKING,
            cls.CLAUDE_45_SONNET,
            cls.CLAUDE_45_SONNET_THINKING,
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
            "| Model | Description |",
            "| ----- | ----------- |",
        ]

        for model in cls.all():
            attr_name = next(
                (name for name, val in vars(cls).items() if val is model),
                model.tool_name.upper(),
            )
            lines.append(f"| `Models.{attr_name}` | {model.name} - {model.description} |")

        return "\n".join(lines)
