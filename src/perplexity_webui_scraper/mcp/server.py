"""MCP server implementation using FastMCP."""

from __future__ import annotations

from os import environ
from typing import Any, Literal

from fastmcp import FastMCP

from perplexity_webui_scraper.config import ClientConfig, ConversationConfig
from perplexity_webui_scraper.core import Perplexity
from perplexity_webui_scraper.enums import CitationMode, SearchFocus, SourceFocus
from perplexity_webui_scraper.models import Model, Models


mcp = FastMCP(
    "perplexity-webui-scraper",
    instructions=(
        "Search the web with Perplexity AI using any model available in the user's account. "
        "Use pplx_list_models to get current model ids, then call pplx_search with the selected model. "
        "All search tools support source_focus: web, academic, social, finance, all."
    ),
)

SOURCE_FOCUS_MAP = {
    "web": [SourceFocus.WEB],
    "academic": [SourceFocus.ACADEMIC],
    "social": [SourceFocus.SOCIAL],
    "finance": [SourceFocus.FINANCE],
    "all": [SourceFocus.WEB, SourceFocus.ACADEMIC, SourceFocus.SOCIAL, SourceFocus.FINANCE],
}

SourceFocusName = Literal["web", "academic", "social", "finance", "all"]
CitationModeName = Literal["default", "markdown", "clean"]

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


def _resolve_model(model: str | Model) -> Model:
    if isinstance(model, Model):
        return model

    client = _get_client()
    return Models.from_identifier(model, available_models=client.available_models())


def _ask(
    query: str,
    model: str | Model = "default",
    source_focus: SourceFocusName = "web",
    citation_mode: CitationModeName = "default",
    files: list[str] | None = None,
) -> dict[str, Any]:
    """Execute a query with any available model."""

    client = _get_client()
    sources = SOURCE_FOCUS_MAP.get(source_focus, [SourceFocus.WEB])
    resolved_model = _resolve_model(model)
    resolved_citation_mode = CitationMode(citation_mode)

    try:
        conversation = client.create_conversation(
            ConversationConfig(
                model=resolved_model,
                citation_mode=resolved_citation_mode,
                search_focus=SearchFocus.WEB,
                source_focus=sources,
            )
        )

        conversation.ask(query, files=files)
        answer = conversation.answer or "No answer received"
        citations = [
            {
                "index": index,
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
            }
            for index, result in enumerate(conversation.search_results, 1)
        ]

        return {
            "answer": answer,
            "model": {
                "id": resolved_model.identifier,
                "name": resolved_model.name,
                "mode": resolved_model.mode,
                "source": resolved_model.source,
            },
            "citations": citations,
            "conversation_uuid": conversation.uuid,
        }

    except Exception as error:
        return {"error": str(error), "model": resolved_model.identifier}


@mcp.tool(
    name="pplx_list_models",
    description="List currently available Perplexity model ids from the live frontend model registry.",
)
def list_models(refresh: bool = False) -> list[dict[str, str]]:
    client = _get_client()
    return [
        {
            "id": model.identifier,
            "name": model.name,
            "description": model.description,
            "mode": model.mode,
            "tier": model.subscription_tier,
            "source": model.source,
        }
        for model in client.available_models(refresh=refresh)
    ]


@mcp.tool(
    name="pplx_search",
    description="Search Perplexity with any available model id. Call pplx_list_models for current ids.",
)
def search(
    query: str,
    model: str = "default",
    source_focus: SourceFocusName = "web",
    citation_mode: CitationModeName = "default",
    files: list[str] | None = None,
) -> dict[str, Any]:
    return _ask(query, model=model, source_focus=source_focus, citation_mode=citation_mode, files=files)


def _create_tool_function(model: Model) -> None:
    """Dynamically create and register a tool for a model."""

    @mcp.tool(name=model.tool_name, description=f"{model.name} - {model.description}")
    def tool_fn(query: str, source_focus: SourceFocusName = "web") -> str:
        result = _ask(query, model, source_focus)
        if "error" in result:
            return f"Error: {result['error']}"

        response_parts = [str(result.get("answer") or "No answer received")]
        citations = result.get("citations") or []
        if citations:
            response_parts.append("\n\nCitations:")
            response_parts.extend(f"\n[{citation['index']}]: {citation.get('url') or ''}" for citation in citations)

        return "".join(response_parts)


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
