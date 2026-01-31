"""Response types and data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict


class Coordinates(BaseModel):
    """Geographic coordinates (lat/lng)."""

    model_config = ConfigDict(frozen=True)

    latitude: float
    longitude: float


class SearchResultItem(BaseModel):
    """A single search result."""

    model_config = ConfigDict(frozen=True)

    title: str | None = None
    snippet: str | None = None
    url: str | None = None


class Response(BaseModel):
    """Response from Perplexity AI."""

    title: str | None = None
    answer: str | None = None
    chunks: list[str] = []
    last_chunk: str | None = None
    search_results: list[SearchResultItem] = []
    conversation_uuid: str | None = None
    raw_data: dict[str, Any] = {}


@dataclass(frozen=True, slots=True)
class _FileInfo:
    """Internal file info for uploads."""

    path: str
    size: int
    mimetype: str
    is_image: bool
