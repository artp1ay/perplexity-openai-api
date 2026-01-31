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

# From GitHub dev branch (latest features)
uv add git+https://github.com/henrique-coder/perplexity-webui-scraper.git@dev
```

### As MCP Server

No installation required - `uvx` handles everything automatically:

```bash
# From PyPI (stable)
uvx --from perplexity-webui-scraper[mcp] perplexity-webui-scraper-mcp

# From GitHub dev branch (latest features)
uvx --from "perplexity-webui-scraper[mcp] @ git+https://github.com/henrique-coder/perplexity-webui-scraper.git@dev" perplexity-webui-scraper-mcp

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
    model=Models.DEEP_RESEARCH,
    source_focus=[SourceFocus.WEB, SourceFocus.ACADEMIC],
    language="en-US",
    coordinates=Coordinates(latitude=12.3456, longitude=-98.7654),
)

conversation = client.create_conversation(config)
conversation.ask("Latest AI research", files=["paper.pdf"])
```

## API Reference

### `Perplexity(session_token, config?)`

| Parameter       | Type           | Description        |
| --------------- | -------------- | ------------------ |
| `session_token` | `str`          | Browser cookie     |
| `config`        | `ClientConfig` | Timeout, TLS, etc. |

### `Conversation.ask(query, model?, files?, citation_mode?, stream?)`

| Parameter       | Type                    | Default       | Description         |
| --------------- | ----------------------- | ------------- | ------------------- |
| `query`         | `str`                   | -             | Question (required) |
| `model`         | `Model`                 | `Models.BEST` | AI model            |
| `files`         | `list[str \| PathLike]` | `None`        | File paths          |
| `citation_mode` | `CitationMode`          | `CLEAN`       | Citation format     |
| `stream`        | `bool`                  | `False`       | Enable streaming    |

### Models

| Model                              | Description                                                               |
| ---------------------------------- | ------------------------------------------------------------------------- |
| `Models.BEST`                      | Automatically selects the best model based on the query                   |
| `Models.DEEP_RESEARCH`             | Create in-depth reports with more sources, charts, and advanced reasoning |
| `Models.CREATE_FILES_AND_APPS`     | Turn your ideas into docs, slides, dashboards, and more                   |
| `Models.SONAR`                     | Perplexity's latest model                                                 |
| `Models.GPT_52`                    | GPT-5.2 - OpenAI's latest model                                           |
| `Models.GPT_52_THINKING`           | GPT-5.2 - OpenAI's latest model (thinking)                                |
| `Models.CLAUDE_45_SONNET`          | Claude Sonnet 4.5 - Anthropic's fast model                                |
| `Models.CLAUDE_45_SONNET_THINKING` | Claude Sonnet 4.5 - Anthropic's fast model (thinking)                     |
| `Models.CLAUDE_45_OPUS`            | Claude Opus 4.5 - Anthropic's Opus reasoning model                        |
| `Models.CLAUDE_45_OPUS_THINKING`   | Claude Opus 4.5 - Anthropic's Opus reasoning model (thinking)             |
| `Models.GEMINI_3_FLASH`            | Gemini 3 Flash - Google's fast model                                      |
| `Models.GEMINI_3_FLASH_THINKING`   | Gemini 3 Flash - Google's fast model (thinking)                           |
| `Models.GEMINI_3_PRO_THINKING`     | Gemini 3 Pro - Google's most advanced model (thinking)                    |
| `Models.GROK_41`                   | Grok 4.1 - xAI's latest model                                             |
| `Models.GROK_41_THINKING`          | Grok 4.1 - xAI's latest model (thinking)                                  |
| `Models.KIMI_K25_THINKING`         | Kimi K2.5 - Moonshot AI's latest model                                    |

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

Each AI model is exposed as a separate tool - enable only the ones you need to reduce agent context size.

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
        "perplexity-webui-scraper[mcp]",
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
        "perplexity-webui-scraper[mcp] @ git+https://github.com/henrique-coder/perplexity-webui-scraper.git@dev",
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

Each tool uses a specific AI model. Enable only the ones you need:

| Tool                                | Model                  | Description                                   |
| ----------------------------------- | ---------------------- | --------------------------------------------- |
| `perplexity_ask`                    | Best                   | Auto-selects best model based on query        |
| `perplexity_deep_research`          | Deep Research          | In-depth reports with more sources and charts |
| `perplexity_sonar`                  | Sonar                  | Perplexity's latest model                     |
| `perplexity_gpt52`                  | GPT-5.2                | OpenAI's latest model                         |
| `perplexity_gpt52_thinking`         | GPT-5.2 Thinking       | OpenAI's latest model (thinking)              |
| `perplexity_claude_sonnet`          | Claude Sonnet 4.5      | Anthropic's fast model                        |
| `perplexity_claude_sonnet_thinking` | Claude Sonnet Thinking | Anthropic's fast model (thinking)             |
| `perplexity_gemini_flash`           | Gemini 3 Flash         | Google's fast model                           |
| `perplexity_gemini_flash_thinking`  | Gemini Flash Thinking  | Google's fast model (thinking)                |
| `perplexity_gemini_pro_thinking`    | Gemini 3 Pro           | Google's most advanced model (thinking)       |
| `perplexity_grok`                   | Grok 4.1               | xAI's latest model                            |
| `perplexity_grok_thinking`          | Grok 4.1 Thinking      | xAI's latest model (thinking)                 |
| `perplexity_kimi_thinking`          | Kimi K2.5              | Moonshot AI's latest model                    |

**All tools support `source_focus`:** `web`, `academic`, `social`, `finance`, `all`

## Disclaimer

This is an **unofficial** library. It uses internal APIs that may change without notice. Use at your own risk.

By using this library, you agree to Perplexity AI's Terms of Service.
