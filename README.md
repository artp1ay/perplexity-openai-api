# Perplexity OpenAI-Compatible API Server

Transform Perplexity AI into a drop-in replacement for OpenAI's API. This server bridges the gap between Perplexity's powerful search-augmented intelligence and applications built for OpenAI's standard interface. Deploy in seconds with Docker, no code changes required. 
It is forked from [henrique-coder/perplexity-webui-scraper](https://github.com/henrique-coder/perplexity-webui-scraper) and uses Python and FastAPI to create a RESTful API server.


### Features

- Models are automatically discovered from Perplexity.
- One-click deployment with Docker
- Request rate limiting 
- OpenAI-compatible `tools` / `tool_calls` support for BoltAI Web Browsing / `web_fetch`

## Quick Start

### Docker (Recommended)

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Add your Perplexity session token to .env

# 3. Start the server
docker-compose up -d

# 4. Test
curl http://localhost:8000/health
curl http://localhost:8000/v1/models
```

### Manual

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Copy and configure .env
cp .env.example .env
# Edit .env with your session token

# Run
python openai_server.py
```

## Getting Your Session Token

1. Log in at [perplexity.ai](https://www.perplexity.ai)
2. Open DevTools (F12) → Application → Cookies
3. Copy `__Secure-next-auth.session-token` value
4. Add to `.env`: `PERPLEXITY_SESSION_TOKEN=your_token`

## API Usage

The server is 100% OpenAI API compatible:

```python
import openai

client = openai.OpenAI(
    api_key="your-api-key",  # Optional
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="perplexity-auto",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "perplexity-auto", "messages": [{"role": "user", "content": "Hello!"}]}'
```

### BoltAI Web Browsing / Web Fetch

BoltAI's Web Browsing plugin works through Function Calling. This server detects web-fetch-like tools
(`web_fetch`, Web Browsing, fetch URL, read webpage, etc.) and returns OpenAI-compatible `tool_calls`
when the latest user message contains HTTP(S) URLs. BoltAI then fetches the pages locally and sends the
tool result back; the server includes that result in the Perplexity prompt as full context.

Enable the Web Browsing plugin in BoltAI and ask for a specific page, for example:

```text
Read https://example.com and summarize the page.
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completions |
| `/v1/models` | GET | List available models |
| `/v1/models/refresh` | POST | Refresh models from Perplexity |
| `/conversations` | GET | List conversations |
| `/stats` | GET | Server statistics |
| `/health` | GET | Health check |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PERPLEXITY_SESSION_TOKEN` | - | Required: Session token |
| `OPENAI_API_KEY` | - | Optional: API key for auth |
| `PORT` | 8000 | Server port |
| `LOG_LEVEL` | INFO | Logging level |
| `ENABLE_RATE_LIMITING` | true | Enable rate limiting |
| `REQUESTS_PER_MINUTE` | 60 | Rate limit |
| `CONVERSATION_TIMEOUT` | 3600 | Session timeout (seconds) |
| `DEFAULT_MODEL` | perplexity-auto | Default model |

## Models

Models are automatically fetched from Perplexity. Common models include:

- `perplexity-auto` - Auto-select best model
- `perplexity-sonar` - Fast responses
- `perplexity-research` - Deep research
- GPT, Claude, Gemini, Grok models via Perplexity

Use `/v1/models` to see all available models.

## License

MIT

## Disclaimer

This is an unofficial implementation using internal Perplexity APIs. Use at your own risk.
