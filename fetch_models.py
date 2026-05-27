#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Optional
from datetime import datetime

try:
    from curl_cffi.requests import Session
except ImportError:
    print("Error: curl_cffi is required. Install it with: pip install curl_cffi")
    sys.exit(1)


# Constants
API_BASE_URL = "https://www.perplexity.ai"
SESSION_COOKIE_NAME = "__Secure-next-auth.session-token"

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@dataclass
class ModelInfo:
    """Information about a Perplexity model."""

    identifier: str
    name: str
    description: str = ""
    mode: str = "copilot"
    provider: str = "unknown"
    is_pro: bool = False
    supports_reasoning: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PerplexityModelsFetcher:
    """Fetches available models from Perplexity's web interface."""

    def __init__(self, session_token: str):
        """Initialize the fetcher with a session token.

        Args:
            session_token: Perplexity session cookie value
        """
        self.session_token = session_token
        self._session: Optional[Session] = None
        self._models: list[ModelInfo] = []

    def _get_session(self) -> Session:
        """Get or create HTTP session."""
        if self._session is None:
            self._session = Session(
                headers={
                    **DEFAULT_HEADERS,
                    "Referer": f"{API_BASE_URL}/",
                    "Origin": API_BASE_URL,
                },
                cookies={SESSION_COOKIE_NAME: self.session_token},
                timeout=30,
                impersonate="chrome",
            )
        return self._session

    def _extract_models_from_html(self, html: str) -> list[ModelInfo]:
        """Extract model information from the page HTML/JS."""
        models: list[ModelInfo] = []

        # Pattern to find model configurations in the JavaScript
        # Perplexity typically embeds model info in __NEXT_DATA__ or similar
        next_data_pattern = (
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        )
        next_data_match = re.search(next_data_pattern, html, re.DOTALL)

        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                models.extend(self._parse_next_data(data))
            except json.JSONDecodeError:
                pass

        # Also look for model identifiers in other script tags
        # Common patterns for model IDs in Perplexity
        model_patterns = [
            # Match model identifier patterns
            r'"identifier"\s*:\s*"([a-z0-9_]+)"',
            r'"model"\s*:\s*"([a-z0-9_]+)"',
            r'modelId["\']?\s*[:=]\s*["\']([a-z0-9_]+)["\']',
        ]

        found_ids = set()
        for pattern in model_patterns:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                model_id = match.group(1)
                if self._is_valid_model_id(model_id):
                    found_ids.add(model_id)

        # Add any newly found models
        existing_ids = {m.identifier for m in models}
        for model_id in found_ids:
            if model_id not in existing_ids:
                models.append(self._create_model_info(model_id))

        return models

    def _parse_next_data(self, data: dict) -> list[ModelInfo]:
        """Parse __NEXT_DATA__ JSON for model information."""
        models: list[ModelInfo] = []

        # Recursively search for model configurations
        def search_dict(d: dict, depth: int = 0) -> None:
            if depth > 10:  # Prevent infinite recursion
                return

            for key, value in d.items():
                if isinstance(value, dict):
                    # Check if this looks like a model definition
                    if "identifier" in value or "modelId" in value:
                        model_id = value.get("identifier") or value.get("modelId")
                        if model_id and self._is_valid_model_id(model_id):
                            models.append(
                                ModelInfo(
                                    identifier=model_id,
                                    name=value.get("name", model_id),
                                    description=value.get("description", ""),
                                    mode=value.get("mode", "copilot"),
                                    provider=value.get("provider", "unknown"),
                                    is_pro=value.get("isPro", False),
                                    supports_reasoning="thinking" in model_id.lower()
                                    or "reasoning" in model_id.lower(),
                                )
                            )
                    search_dict(value, depth + 1)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            search_dict(item, depth + 1)

        search_dict(data)
        return models

    def _is_valid_model_id(self, model_id: str) -> bool:
        """Check if a string looks like a valid model identifier."""
        if not model_id or len(model_id) < 3:
            return False

        # Known model ID patterns
        valid_patterns = [
            r"^pplx_",
            r"^gpt\d",
            r"^claude",
            r"^gemini",
            r"^grok",
            r"^sonar",
            r"^experimental",
            r"^kimi",
            r"^llama",
            r"^mistral",
            r"^deepseek",
        ]

        # Exclude common false positives
        exclude_patterns = [
            r"^api_",
            r"^user_",
            r"^session",
            r"^token",
            r"^auth",
            r"^config",
        ]

        for pattern in exclude_patterns:
            if re.match(pattern, model_id, re.IGNORECASE):
                return False

        for pattern in valid_patterns:
            if re.match(pattern, model_id, re.IGNORECASE):
                return True

        return False

    def _create_model_info(self, model_id: str) -> ModelInfo:
        """Create ModelInfo from a model identifier."""
        name = self._infer_model_name(model_id)
        provider = self._infer_provider(model_id)

        return ModelInfo(
            identifier=model_id,
            name=name,
            description=f"{provider} model",
            mode="copilot",
            provider=provider,
            is_pro="pro" in model_id.lower() or "alpha" in model_id.lower(),
            supports_reasoning="thinking" in model_id.lower()
            or "reasoning" in model_id.lower(),
        )

    def _infer_model_name(self, model_id: str) -> str:
        """Infer a human-readable name from model ID."""
        name_mappings = {
            "pplx_beta": "Perplexity Labs",
            "pplx_alpha": "Perplexity Research",
            "pplx_pro": "Perplexity Pro (Auto)",
            "experimental": "Sonar",
            "gpt51": "GPT-5.1",
            "gpt52": "GPT-5.2",
            "gpt51_thinking": "GPT-5.1 Thinking",
            "claude45sonnet": "Claude 4.5 Sonnet",
            "claude45sonnetthinking": "Claude 4.5 Sonnet Thinking",
            "claudeopus45": "Claude Opus 4.5",
            "gemini30pro": "Gemini 3.0 Pro Thinking",
            "grok41nonreasoning": "Grok 4.1",
            "kimik2thinking": "Kimi K2 Thinking",
        }

        return name_mappings.get(model_id, model_id.replace("_", " ").title())

    def _infer_provider(self, model_id: str) -> str:
        """Infer the model provider from model ID."""
        model_id_lower = model_id.lower()

        if model_id_lower.startswith("pplx") or model_id_lower == "experimental":
            return "Perplexity"
        elif model_id_lower.startswith("gpt"):
            return "OpenAI"
        elif model_id_lower.startswith("claude"):
            return "Anthropic"
        elif model_id_lower.startswith("gemini"):
            return "Google"
        elif model_id_lower.startswith("grok"):
            return "xAI"
        elif model_id_lower.startswith("kimi"):
            return "Moonshot AI"
        elif model_id_lower.startswith("llama"):
            return "Meta"
        elif model_id_lower.startswith("mistral"):
            return "Mistral AI"
        elif model_id_lower.startswith("deepseek"):
            return "DeepSeek"
        else:
            return "Unknown"

    def fetch_models(self) -> list[ModelInfo]:
        """Fetch available models from Perplexity.

        Returns:
            List of available models
        """
        session = self._get_session()

        # Fetch the main page to get model information
        try:
            response = session.get(API_BASE_URL)
            response.raise_for_status()

            models = self._extract_models_from_html(response.text)

            # If we didn't find models from HTML, try the settings/API endpoint
            if not models:
                models = self._fetch_from_settings()

            # If still no models, use known defaults
            if not models:
                models = self._get_default_models()

            self._models = models
            return models

        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Return default models on error
            self._models = self._get_default_models()
            return self._models

    def _fetch_from_settings(self) -> list[ModelInfo]:
        """Try to fetch models from settings or API endpoints."""
        session = self._get_session()
        models: list[ModelInfo] = []

        # Try various endpoints that might contain model info
        endpoints = [
            "/api/auth/session",
            "/api/user/settings",
        ]

        for endpoint in endpoints:
            try:
                response = session.get(f"{API_BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    # Look for model information in the response
                    if isinstance(data, dict):
                        for key in ["models", "availableModels", "supportedModels"]:
                            if key in data:
                                model_list = data[key]
                                if isinstance(model_list, list):
                                    for m in model_list:
                                        if isinstance(m, str):
                                            models.append(self._create_model_info(m))
                                        elif isinstance(m, dict) and "identifier" in m:
                                            models.append(
                                                ModelInfo(
                                                    identifier=m["identifier"],
                                                    name=m.get("name", m["identifier"]),
                                                    description=m.get(
                                                        "description", ""
                                                    ),
                                                    mode=m.get("mode", "copilot"),
                                                    provider=self._infer_provider(
                                                        m["identifier"]
                                                    ),
                                                )
                                            )
            except Exception:
                continue

        return models

    def _get_default_models(self) -> list[ModelInfo]:
        """Return known default models as fallback."""
        return [
            ModelInfo(
                "pplx_pro",
                "Perplexity Pro (Auto)",
                "Auto-selects the best model",
                "copilot",
                "Perplexity",
                True,
            ),
            ModelInfo(
                "pplx_alpha",
                "Perplexity Research",
                "Deep research mode",
                "copilot",
                "Perplexity",
                True,
            ),
            ModelInfo(
                "pplx_beta",
                "Perplexity Labs",
                "Experimental features",
                "copilot",
                "Perplexity",
                True,
            ),
            ModelInfo(
                "experimental",
                "Sonar",
                "Fast model for quick queries",
                "copilot",
                "Perplexity",
                False,
            ),
            ModelInfo(
                "gpt51", "GPT-5.1", "OpenAI's GPT-5.1", "copilot", "OpenAI", True
            ),
            ModelInfo(
                "gpt52", "GPT-5.2", "OpenAI's GPT-5.2", "copilot", "OpenAI", True
            ),
            ModelInfo(
                "gpt51_thinking",
                "GPT-5.1 Thinking",
                "GPT-5.1 with reasoning",
                "copilot",
                "OpenAI",
                True,
                True,
            ),
            ModelInfo(
                "claude45sonnet",
                "Claude 4.5 Sonnet",
                "Anthropic's Claude 4.5 Sonnet",
                "copilot",
                "Anthropic",
                True,
            ),
            ModelInfo(
                "claude45sonnetthinking",
                "Claude 4.5 Sonnet Thinking",
                "Claude 4.5 with reasoning",
                "copilot",
                "Anthropic",
                True,
                True,
            ),
            ModelInfo(
                "claudeopus45",
                "Claude Opus 4.5",
                "Anthropic's Claude Opus 4.5",
                "copilot",
                "Anthropic",
                True,
            ),
            ModelInfo(
                "gemini30pro",
                "Gemini 3.0 Pro Thinking",
                "Google's Gemini with reasoning",
                "copilot",
                "Google",
                True,
                True,
            ),
            ModelInfo(
                "grok41nonreasoning",
                "Grok 4.1",
                "xAI's Grok 4.1",
                "copilot",
                "xAI",
                True,
            ),
            ModelInfo(
                "kimik2thinking",
                "Kimi K2 Thinking",
                "Moonshot AI's Kimi K2",
                "copilot",
                "Moonshot AI",
                True,
                True,
            ),
        ]

    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Get a model by its identifier."""
        if not self._models:
            self.fetch_models()

        for model in self._models:
            if model.identifier == model_id:
                return model
        return None

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> "PerplexityModelsFetcher":
        return self

    def __exit__(self, *args) -> None:
        self.close()


def get_available_models(session_token: str) -> list[ModelInfo]:
    """Convenience function to fetch available models.

    Args:
        session_token: Perplexity session cookie value

    Returns:
        List of available models
    """
    with PerplexityModelsFetcher(session_token) as fetcher:
        return fetcher.fetch_models()
