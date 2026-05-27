<div align="center">

# Perplexity WebUI Scraper

Python scraper to extract AI responses from [Perplexity's](https://www.perplexity.ai) web interface.

[![PyPI](https://img.shields.io/pypi/v/perplexity-webui-scraper?color=blue)](https://pypi.org/project/perplexity-webui-scraper)
[![Python](https://img.shields.io/pypi/pyversions/perplexity-webui-scraper)](https://pypi.org/project/perplexity-webui-scraper)
[![License](https://img.shields.io/github/license/henrique-coder/perplexity-webui-scraper?color=green)](./LICENSE)

</div>

---

## Installation

### As a Library

```bash
# From PyPI (stable)
uv add perplexity-webui-scraper

# From GitHub prod branch (latest fixes)
uv add git+https://github.com/henrique-coder/perplexity-webui-scraper.git@prod
```

### As MCP Server

No installation required - `uvx` handles everything automatically:

```bash
# From PyPI (stable)
uvx --from perplexity-webui-scraper[mcp]@latest perplexity-webui-scraper-mcp

# From GitHub prod branch (latest fixes)
uvx --from "perplexity-webui-scraper[mcp]@git+https://github.com/henrique-coder/perplexity-webui-scraper.git@prod" perplexity-webui-scraper-mcp

# From local directory (for development)
uv --directory /path/to/perplexity-webui-scraper run perplexity-webui-scraper-mcp
```

## Requirements

- **Perplexity Pro/Max account**
- **Session token** (`__Secure-next-auth.session-token` cookie)

### Getting Your Session Token

#### Option 1: Automatic (CLI Tool)

```bash
uv run get-perplexity-session-token
```

This interactive tool will:

1. Ask for your Perplexity email
2. Send a verification code to your email
3. Accept either a 6-digit code or magic link
4. Extract and display your session token
5. Optionally save it to your `.env` file

#### Option 2: Manual (Browser)

1. Log in at [perplexity.ai](https://www.perplexity.ai)
2. Open DevTools (`F12`) → Application/Storage → Cookies
3. Copy the value of `__Secure-next-auth.session-token`
4. Store in `.env`: `PERPLEXITY_SESSION_TOKEN="your_token"`

## Quick Start

```python
from perplexity_webui_scraper import Perplexity

client = Perplexity(session_token="YOUR_TOKEN")
conversation = client.create_conversation()

conversation.ask("What is quantum computing?")
print(conversation.answer)

# Follow-up (context is preserved)
conversation.ask("Explain it simpler")
print(conversation.answer)
```

### Streaming

```python
for chunk in conversation.ask("Explain AI", stream=True):
    print(chunk.answer)
```

### With Options

```python
from perplexity_webui_scraper import (
    ConversationConfig,
    Coordinates,
    Models,
    SourceFocus,
)

config = ConversationConfig(
    model="pplx_alpha",
    source_focus=[SourceFocus.WEB, SourceFocus.ACADEMIC],
    language="en-US",
    coordinates=Coordinates(latitude=12.3456, longitude=-98.7654),
)

conversation = client.create_conversation(config)
conversation.ask("Latest AI research", files=["paper.pdf"])
```

### Available Models

```python
models = client.available_models(refresh=True)
for model in models:
    print(model.identifier, model.name, model.mode)

conversation.ask("Compare current AI search engines", model="default")
```

Model metadata is discovered from Perplexity's live frontend assets and cached for one hour by default.
The bundled `Models.*` constants remain as offline fallbacks, but runtime code can use any current model id
returned by `client.available_models()`.

## API Reference

### `Perplexity(session_token, config?)`

| Parameter       | Type           | Description        |
| --------------- | -------------- | ------------------ |
| `session_token` | `str`          | Browser cookie     |
| `config`        | `ClientConfig` | Timeout, TLS, etc. |

### `Perplexity.available_models(refresh?, cache_ttl?)`

Returns the currently advertised Perplexity models as `Model` objects. Set `refresh=True` to bypass the
in-process cache.

### `Conversation.ask(query, model?, files?, citation_mode?, stream?)`

| Parameter       | Type                    | Default       | Description         |
| --------------- | ----------------------- | ------------- | ------------------- |
| `query`         | `str`                   | -             | Question (required) |
| `model`         | `Model \| str`          | `Models.BEST` | AI model or model id |
| `files`         | `list[str \| PathLike]` | `None`        | File paths          |
| `citation_mode` | `CitationMode`          | `CLEAN`       | Citation format     |
| `stream`        | `bool`                  | `False`       | Enable streaming    |

### Models

Use `client.available_models()` for the current live list. `Models.all()` returns bundled fallback models
for offline usage and backward compatibility.

### CitationMode

| Mode       | Output                |
| ---------- | --------------------- |
| `DEFAULT`  | `text[1]`             |
| `MARKDOWN` | `text[1](url)`        |
| `CLEAN`    | `text` (no citations) |

### ConversationConfig

| Parameter         | Default       | Description        |
| ----------------- | ------------- | ------------------ |
| `model`           | `Models.BEST` | Default model      |
| `citation_mode`   | `CLEAN`       | Citation format    |
| `save_to_library` | `False`       | Save to library    |
| `search_focus`    | `WEB`         | Search type        |
| `source_focus`    | `WEB`         | Source types       |
| `time_range`      | `ALL`         | Time filter        |
| `language`        | `"en-US"`     | Response language  |
| `timezone`        | `None`        | Timezone           |
| `coordinates`     | `None`        | Location (lat/lng) |

## Exceptions

| Exception                          | Description                                        |
| ---------------------------------- | -------------------------------------------------- |
| `PerplexityError`                  | Base exception for all library errors              |
| `HTTPError`                        | HTTP error with status code and response body      |
| `AuthenticationError`              | Session token is invalid or expired (HTTP 401/403) |
| `RateLimitError`                   | Rate limit exceeded (HTTP 429)                     |
| `FileUploadError`                  | File upload failed                                 |
| `FileValidationError`              | File validation failed (size, type, etc.)          |
| `ResearchClarifyingQuestionsError` | Research mode asking clarifying questions          |
| `ResponseParsingError`             | API response could not be parsed                   |
| `StreamingError`                   | Error during streaming response                    |

## MCP Server (Model Context Protocol)

The library includes an MCP server for AI assistants like Claude Desktop and Antigravity.

The server exposes a universal `pplx_search` tool that accepts any live model id. Per-model tools are still
registered as backward-compatible aliases.

### Configuration

Add to your MCP config file (no installation required):

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "perplexity-webui-scraper": {
      "command": "uvx",
      "args": [
        "--from",
        "perplexity-webui-scraper[mcp]@latest",
        "perplexity-webui-scraper-mcp"
      ],
      "env": {
        "PERPLEXITY_SESSION_TOKEN": "your_token_here"
      }
    }
  }
}
```

**From GitHub dev branch:**

```json
{
  "mcpServers": {
    "perplexity-webui-scraper": {
      "command": "uvx",
      "args": [
        "--from",
        "perplexity-webui-scraper[mcp]@git+https://github.com/henrique-coder/perplexity-webui-scraper.git@prod",
        "perplexity-webui-scraper-mcp"
      ],
      "env": {
        "PERPLEXITY_SESSION_TOKEN": "your_token_here"
      }
    }
  }
}
```

**From local directory (for development):**

```json
{
  "mcpServers": {
    "perplexity-webui-scraper": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/perplexity-webui-scraper",
        "run",
        "perplexity-webui-scraper-mcp"
      ],
      "env": {
        "PERPLEXITY_SESSION_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Available Tools

| Tool               | Description                                                              |
| ------------------ | ------------------------------------------------------------------------ |
| `pplx_list_models` | Returns current model ids from the live Perplexity frontend model list   |
| `pplx_search`      | Searches with any model id returned by `pplx_list_models`                |
| `pplx_ask`, etc.   | Backward-compatible aliases for bundled fallback models                  |

`pplx_search` supports:

- `model`: any current model id, model name, or bundled tool name
- `source_focus`: `web`, `academic`, `social`, `finance`, `all`
- `citation_mode`: `default`, `markdown`, `clean`
- `files`: optional local file paths

## Disclaimer

This is an **unofficial** library. It uses internal APIs that may change without notice. Use at your own risk.

By using this library, you agree to Perplexity AI's Terms of Service.
