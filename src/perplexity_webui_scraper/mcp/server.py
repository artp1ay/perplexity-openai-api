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


def _create_tool_function(model: Model) -> None:
    """Dynamically create and register a tool for a model."""

    @mcp.tool(name=model.tool_name, description=f"{model.name} - {model.description}")
    def tool_fn(query: str, source_focus: SourceFocusName = "web") -> str:
        return _ask(query, model, source_focus)


def _register_all_tools() -> None:
    """Register all model tools dynamically."""

    for model in Models.all():
        _create_tool_function(model)


_register_all_tools()


def main() -> None:
    """Run the MCP server."""

    mcp.run()


if __name__ == "__main__":
    main()
