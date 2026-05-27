"""Extract AI responses from Perplexity's web interface."""

from importlib import metadata

from .config import ClientConfig, ConversationConfig
from .core import Conversation, Perplexity
from .enums import CitationMode, LogLevel, SearchFocus, SourceFocus, TimeRange
from .exceptions import (
    AuthenticationError,
    FileUploadError,
    FileValidationError,
    HTTPError,
    PerplexityError,
    RateLimitError,
    ResearchClarifyingQuestionsError,
    ResponseParsingError,
    StreamingError,
)
from .models import Model, Models
from .types import Coordinates, Response, SearchResultItem
from .fetch_models import ModelInfo, PerplexityModelsFetcher, get_available_models


ConversationConfig.model_rebuild()


__version__: str = metadata.version("perplexity-webui-scraper")
__all__: list[str] = [
    "AuthenticationError",
    "CitationMode",
    "ClientConfig",
    "Conversation",
    "ConversationConfig",
    "Coordinates",
    "FileUploadError",
    "FileValidationError",
    "get_available_models",
    "HTTPError",
    "LogLevel",
    "Model",
    "ModelInfo",
    "Models",
    "Perplexity",
    "PerplexityError",
    "PerplexityModelsFetcher",
    "RateLimitError",
    "ResearchClarifyingQuestionsError",
    "Response",
    "ResponseParsingError",
    "SearchFocus",
    "SearchResultItem",
    "SourceFocus",
    "StreamingError",
    "TimeRange",
]
