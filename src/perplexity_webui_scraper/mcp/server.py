"""MCP server implementation using FastMCP."""

from __future__ import annotations

from os import environ
from typing import Literal

from fastmcp import FastMCP

from perplexity_webui_scraper.config import ClientConfig, ConversationConfig
from perplexity_webui_scraper.core import Perplexity
from perplexity_webui_scraper.enums import CitationMode, SearchFocus, SourceFocus
from perplexity_webui_scraper.models import Model, Models


mcp = FastMCP(
    "perplexity-webui-scraper",
    instructions=(
        "Search the web with Perplexity AI using premium models. "
        "Each tool uses a specific AI model - enable only the ones you need. "
        "All tools support source_focus: web, academic, social, finance, all."
    ),
)

SOURCE_FOCUS_MAP = {
    "web": [SourceFocus.WEB],
    "academic": [SourceFocus.ACADEMIC],
    "social": [SourceFocus.SOCIAL],
    "finance": [SourceFocus.FINANCE],
    "all": [SourceFocus.WEB, SourceFocus.ACADEMIC, SourceFocus.SOCIAL],
}

SourceFocusName = Literal["web", "academic", "social", "finance", "all"]

_client: Perplexity | None = None


def _get_client() -> Perplexity:
    """Get or create Perplexity client."""

    global _client  # noqa: PLW0603

    if _client is None:
        token = environ.get("PERPLEXITY_SESSION_TOKEN", "")

        if not token:
            raise ValueError(
                "PERPLEXITY_SESSION_TOKEN environment variable is required. "
                "Set it with: export PERPLEXITY_SESSION_TOKEN='your_token_here'"
            )

        _client = Perplexity(token, config=ClientConfig())

    return _client


def _ask(query: str, model: Model, source_focus: SourceFocusName = "web") -> str:
    """Execute a query with a specific model."""

    client = _get_client()
    sources = SOURCE_FOCUS_MAP.get(source_focus, [SourceFocus.WEB])

    try:
        conversation = client.create_conversation(
            ConversationConfig(
                model=model,
                citation_mode=CitationMode.DEFAULT,
                search_focus=SearchFocus.WEB,
                source_focus=sources,
            )
        )

        conversation.ask(query)
        answer = conversation.answer or "No answer received"

        response_parts = [answer]

        if conversation.search_results:
            response_parts.append("\n\nCitations:")

            for i, result in enumerate(conversation.search_results, 1):
                url = result.url or ""
                response_parts.append(f"\n[{i}]: {url}")

        return "".join(response_parts)

    except Exception as error:
        return f"Error: {error!s}"


@mcp.tool
def pplx_ask(query: str, source_focus: SourceFocusName = "web") -> str:
    """Ask a question with real-time data from the internet (auto-selects best model)."""

    return _ask(query, Models.BEST, source_focus)


@mcp.tool
def pplx_deep_research(query: str, source_focus: SourceFocusName = "web") -> str:
    """Deep Research - In-depth reports with more sources, charts, and advanced reasoning."""

    return _ask(query, Models.DEEP_RESEARCH, source_focus)


@mcp.tool
def pplx_sonar(query: str, source_focus: SourceFocusName = "web") -> str:
    """Sonar - Perplexity's latest model."""

    return _ask(query, Models.SONAR, source_focus)


@mcp.tool
def pplx_gpt52(query: str, source_focus: SourceFocusName = "web") -> str:
    """GPT-5.2 - OpenAI's latest model."""

    return _ask(query, Models.GPT_52, source_focus)


@mcp.tool
def pplx_gpt52_thinking(query: str, source_focus: SourceFocusName = "web") -> str:
    """GPT-5.2 Thinking - OpenAI's latest model with extended thinking."""

    return _ask(query, Models.GPT_52_THINKING, source_focus)


@mcp.tool
def pplx_claude_sonnet(query: str, source_focus: SourceFocusName = "web") -> str:
    """Claude Sonnet 4.5 - Anthropic's fast model."""

    return _ask(query, Models.CLAUDE_45_SONNET, source_focus)


@mcp.tool
def pplx_claude_sonnet_think(query: str, source_focus: SourceFocusName = "web") -> str:
    """Claude Sonnet 4.5 Thinking - Anthropic's fast model with extended thinking."""

    return _ask(query, Models.CLAUDE_45_SONNET_THINKING, source_focus)


@mcp.tool
def pplx_gemini_flash(query: str, source_focus: SourceFocusName = "web") -> str:
    """Gemini 3 Flash - Google's fast model."""

    return _ask(query, Models.GEMINI_3_FLASH, source_focus)


@mcp.tool
def pplx_gemini_flash_think(query: str, source_focus: SourceFocusName = "web") -> str:
    """Gemini 3 Flash Thinking - Google's fast model with extended thinking."""

    return _ask(query, Models.GEMINI_3_FLASH_THINKING, source_focus)


@mcp.tool
def pplx_gemini_pro_think(query: str, source_focus: SourceFocusName = "web") -> str:
    """Gemini 3 Pro Thinking - Google's most advanced model with extended thinking."""

    return _ask(query, Models.GEMINI_3_PRO_THINKING, source_focus)


@mcp.tool
def pplx_grok(query: str, source_focus: SourceFocusName = "web") -> str:
    """Grok 4.1 - xAI's latest model."""

    return _ask(query, Models.GROK_41, source_focus)


@mcp.tool
def pplx_grok_thinking(query: str, source_focus: SourceFocusName = "web") -> str:
    """Grok 4.1 Thinking - xAI's latest model with extended thinking."""

    return _ask(query, Models.GROK_41_THINKING, source_focus)


@mcp.tool
def pplx_kimi_thinking(query: str, source_focus: SourceFocusName = "web") -> str:
    """Kimi K2.5 Thinking - Moonshot AI's latest model."""

    return _ask(query, Models.KIMI_K25_THINKING, source_focus)


def main() -> None:
    """Run the MCP server."""

    mcp.run()


if __name__ == "__main__":
    main()
