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

| Model                              | Description                                                               | Tier |
| ---------------------------------- | ------------------------------------------------------------------------- | ---- |
| `Models.BEST`                      | Pro - Automatically selects the most responsive model based on the query  | pro  |
| `Models.DEEP_RESEARCH`             | Deep research - Fast and thorough for routine research                    | pro  |
| `Models.SONAR`                     | Sonar - Perplexity's latest model                                         | pro  |
| `Models.GEMINI_3_FLASH`            | Gemini 3 Flash - Google's fast model                                      | pro  |
| `Models.GEMINI_3_FLASH_THINKING`   | Gemini 3 Flash Thinking - Google's fast model                             | pro  |
| `Models.GEMINI_31_PRO`             | Gemini 3.1 Pro - Google's latest model                                    | pro  |
| `Models.GEMINI_31_PRO_THINKING`    | Gemini 3.1 Pro Thinking - Google's latest model with thinking             | pro  |
| `Models.GPT_52`                    | GPT-5.2 - OpenAI's latest model                                           | pro  |
| `Models.GPT_52_THINKING`           | GPT-5.2 Thinking - OpenAI's latest model with thinking                    | pro  |
| `Models.CLAUDE_46_SONNET`          | Claude Sonnet 4.6 - Anthropic's fast model                                | pro  |
| `Models.CLAUDE_46_SONNET_THINKING` | Claude Sonnet 4.6 Thinking - Anthropic's newest reasoning model           | pro  |
| `Models.CLAUDE_46_OPUS`            | Claude Opus 4.6 - Anthropic's most advanced model                         | max  |
| `Models.CLAUDE_46_OPUS_THINKING`   | Claude Opus 4.6 Thinking - Anthropic's Opus reasoning model with thinking | max  |
| `Models.GROK_41`                   | Grok 4.1 - xAI's latest model                                             | pro  |
| `Models.GROK_41_THINKING`          | Grok 4.1 Thinking - xAI's latest model                                    | pro  |
| `Models.KIMI_K25_THINKING`         | Kimi K2.5 - Moonshot AI's latest model                                    | pro  |

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

Each tool uses a specific AI model. Enable only the ones you need:

| Tool                      | Model                      | Description                                                        | Tier |
| ------------------------- | -------------------------- | ------------------------------------------------------------------ | ---- |
| `pplx_ask`                | Pro                        | Automatically selects the most responsive model based on the query | pro  |
| `pplx_deep_research`      | Deep research              | Fast and thorough for routine research                             | pro  |
| `pplx_sonar`              | Sonar                      | Perplexity's latest model                                          | pro  |
| `pplx_gemini_flash`       | Gemini 3 Flash             | Google's fast model                                                | pro  |
| `pplx_gemini_flash_think` | Gemini 3 Flash Thinking    | Google's fast model                                                | pro  |
| `pplx_gemini31_pro`       | Gemini 3.1 Pro             | Google's latest model                                              | pro  |
| `pplx_gemini31_pro_think` | Gemini 3.1 Pro Thinking    | Google's latest model with thinking                                | pro  |
| `pplx_gpt54`              | GPT-5.4                    | OpenAI's latest model                                              | pro  |
| `pplx_gpt54_thinking`     | GPT-5.4 Thinking           | OpenAI's latest model with thinking                                | pro  |
| `pplx_claude_s46`         | Claude Sonnet 4.6          | Anthropic's fast model                                             | pro  |
| `pplx_claude_s46_think`   | Claude Sonnet 4.6 Thinking | Anthropic's newest reasoning model                                 | pro  |
| `pplx_claude_o46`         | Claude Opus 4.6            | Anthropic's most advanced model                                    | max  |
| `pplx_claude_o46_think`   | Claude Opus 4.6 Thinking   | Anthropic's Opus reasoning model with thinking                     | max  |
| `pplx_grok41`             | Grok 4.1                   | xAI's latest model                                                 | pro  |
| `pplx_grok41_think`       | Grok 4.1 Thinking          | xAI's latest model                                                 | pro  |
| `pplx_kimi_k25_think`     | Kimi K2.5                  | Moonshot AI's latest model                                         | pro  |

**All tools support `source_focus`:** `web`, `academic`, `social`, `finance`, `all`

## Disclaimer

This is an **unofficial** library. It uses internal APIs that may change without notice. Use at your own risk.

By using this library, you agree to Perplexity AI's Terms of Service.
