"""Enums for configuration options."""

from __future__ import annotations

from enum import Enum


class CitationMode(str, Enum):
    """Citation formatting modes for response text."""

    DEFAULT = "default"
    """Keep original format (e.g., 'text[1]')."""

    MARKDOWN = "markdown"
    """Convert to markdown links (e.g., 'text[1](url)')."""

    CLEAN = "clean"
    """Remove all citation markers."""


class SearchFocus(str, Enum):
    """Search focus types."""

    WEB = "internet"
    """Search the web for information."""

    WRITING = "writing"
    """Focus on writing tasks."""


class SourceFocus(str, Enum):
    """Source focus types for search prioritization."""

    WEB = "web"
    """General web search."""

    ACADEMIC = "scholar"
    """Academic papers and scholarly articles."""

    SOCIAL = "social"
    """Social media (Reddit, Twitter, etc.)."""

    FINANCE = "edgar"
    """SEC EDGAR filings."""


class TimeRange(str, Enum):
    """Time range filters for search results."""

    ALL = ""
    """No time restriction."""

    TODAY = "DAY"
    """Last 24 hours."""

    LAST_WEEK = "WEEK"
    """Last 7 days."""

    LAST_MONTH = "MONTH"
    """Last 30 days."""

    LAST_YEAR = "YEAR"
    """Last 365 days."""


class LogLevel(str, Enum):
    """Logging level configuration."""

    DISABLED = "DISABLED"
    """Disable all logging (default)."""

    DEBUG = "DEBUG"
    """Show all messages including debug info."""

    INFO = "INFO"
    """Show info, warnings, and errors."""

    WARNING = "WARNING"
    """Show warnings and errors only."""

    ERROR = "ERROR"
    """Show errors only."""

    CRITICAL = "CRITICAL"
    """Show critical/fatal errors only."""
