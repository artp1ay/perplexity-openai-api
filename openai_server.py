#!/usr/bin/env python3

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import re
import sys
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, AsyncGenerator, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from perplexity_webui_scraper import (
    CitationMode,
    Conversation,
    ConversationConfig,
    Models,
    Perplexity,
    PerplexityError
)
from perplexity_webui_scraper.models import Model
from fetch_models import ModelInfo as FetchedModelInfo
from fetch_models import PerplexityModelsFetcher


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class ServerConfig:
    """Server configuration loaded from environment variables."""
    
    session_token: str
    api_key: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # Rate Limiting
    requests_per_minute: int = 60
    enable_rate_limiting: bool = True
    
    # Conversations
    conversation_timeout: int = 3600
    max_conversations_per_user: int = 100
    
    # Defaults
    default_model: str = "perplexity-auto"
    default_citation_mode: CitationMode = CitationMode.CLEAN
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        session_token = os.getenv("PERPLEXITY_SESSION_TOKEN")
        if not session_token:
            print("❌ Error: PERPLEXITY_SESSION_TOKEN environment variable is required")
            print("\n📋 To get your session token:")
            print("1. Log in at https://www.perplexity.ai")
            print("2. Open DevTools (F12) → Application → Cookies")
            print("3. Copy the '__Secure-next-auth.session-token' value")
            print("4. Set it: export PERPLEXITY_SESSION_TOKEN='your_token'")
            sys.exit(1)
        
        return cls(
            session_token=session_token,
            api_key=os.getenv("OPENAI_API_KEY"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE", "60")),
            enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
            conversation_timeout=int(os.getenv("CONVERSATION_TIMEOUT", "3600")),
            max_conversations_per_user=int(os.getenv("MAX_CONVERSATIONS_PER_USER", "100")),
            default_model=os.getenv("DEFAULT_MODEL", "perplexity-auto"),
            default_citation_mode=CitationMode[os.getenv("DEFAULT_CITATION_MODE", "CLEAN").upper()],
        )


# =============================================================================
# Dynamic Model Registry
# =============================================================================

class ModelRegistry:
    """Manages available models fetched from Perplexity."""
    
    def __init__(self):
        self._models: list[FetchedModelInfo] = []
        self._mapping: dict[str, Model] = {}
        self._available: list[dict[str, str]] = []
        self._last_fetch: datetime | None = None
        self._refresh_interval = 3600  # 1 hour
    
    def fetch(self, session_token: str) -> None:
        """Fetch available models from Perplexity."""
        logging.info("🔄 Fetching models from Perplexity...")
        
        try:
            with PerplexityModelsFetcher(session_token) as fetcher:
                self._models = fetcher.fetch_models()
            
            self._build_mappings()
            self._last_fetch = datetime.now()
            logging.info(f"✅ Loaded {len(self._models)} models")
            
        except Exception as e:
            logging.error(f"❌ Failed to fetch models: {e}")
            self._use_defaults()
    
    def _build_mappings(self) -> None:
        """Build model mappings and available list."""
        # Static aliases
        self._mapping = {
            "gpt-4": Models.BEST,
            "gpt-4-turbo": Models.BEST,
            "gpt-4o": Models.BEST,
            "perplexity": Models.BEST,
            "perplexity-auto": Models.BEST,
            "auto": Models.BEST,
            "perplexity-sonar": Models.SONAR,
            "perplexity-research": Models.RESEARCH,
            "perplexity-labs": Models.LABS,
            "sonar": Models.SONAR,
            "research": Models.RESEARCH,
            "labs": Models.LABS,
        }
        
        self._available = [
            {"id": "perplexity-auto", "name": "Perplexity Auto", "owned_by": "perplexity"},
            {"id": "perplexity-sonar", "name": "Perplexity Sonar", "owned_by": "perplexity"},
            {"id": "perplexity-research", "name": "Perplexity Research", "owned_by": "perplexity"},
            {"id": "perplexity-labs", "name": "Perplexity Labs", "owned_by": "perplexity"},
        ]
        
        # Add fetched models
        for model in self._models:
            model_obj = Model(identifier=model.identifier, mode=model.mode)
            
            # Add direct identifier
            self._mapping[model.identifier.lower()] = model_obj
            
            # Add aliases
            for alias in self._generate_aliases(model.identifier):
                self._mapping[alias.lower()] = model_obj
            
            # Add to available list
            if not any(m["id"] == model.identifier for m in self._available):
                self._available.append({
                    "id": model.identifier,
                    "name": model.name,
                    "owned_by": model.provider.lower(),
                })
    
    def _generate_aliases(self, identifier: str) -> list[str]:
        """Generate friendly aliases for a model identifier."""
        aliases = []
        id_lower = identifier.lower()
        
        # GPT: gpt51 -> gpt-5.1, gpt-51
        if id_lower.startswith("gpt"):
            match = re.match(r'gpt(\d)(\d)', id_lower)
            if match:
                aliases.extend([f"gpt-{match.group(1)}.{match.group(2)}", f"gpt-{match.group(1)}{match.group(2)}"])
        
        # Claude: claude45sonnet -> claude-4.5-sonnet
        elif id_lower.startswith("claude"):
            if "opus" in id_lower:
                match = re.search(r'opus(\d+)', id_lower)
                if match:
                    v = match.group(1)
                    aliases.extend([f"claude-opus-{v[0]}.{v[1:]}" if len(v) > 1 else f"claude-opus-{v}"])
            elif "sonnet" in id_lower:
                match = re.search(r'(\d+)sonnet', id_lower)
                if match:
                    v = match.group(1)
                    aliases.extend([f"claude-{v[0]}.{v[1:]}-sonnet" if len(v) > 1 else f"claude-{v}-sonnet"])
        
        # Gemini: gemini30pro -> gemini-3-pro
        elif id_lower.startswith("gemini"):
            match = re.search(r'gemini(\d+)pro', id_lower)
            if match:
                v = match.group(1)
                aliases.extend([f"gemini-{v[0]}-pro", f"gemini-{v}-pro"])
        
        # Grok: grok41 -> grok-4.1
        elif id_lower.startswith("grok"):
            match = re.search(r'grok(\d+)', id_lower)
            if match:
                v = match.group(1)
                aliases.extend([f"grok-{v[0]}.{v[1:]}" if len(v) > 1 else f"grok-{v}"])
        
        # Add thinking suffix variants
        if "thinking" in id_lower:
            aliases.extend([f"{a}-thinking" for a in aliases])
        
        return aliases
    
    def _use_defaults(self) -> None:
        """Use default models as fallback."""
        self._models = []
        self._mapping = {
            "perplexity-auto": Models.BEST,
            "perplexity-sonar": Models.SONAR,
            "perplexity-research": Models.RESEARCH,
            "auto": Models.BEST,
        }
        self._available = [
            {"id": "perplexity-auto", "name": "Perplexity Auto", "owned_by": "perplexity"},
            {"id": "perplexity-sonar", "name": "Perplexity Sonar", "owned_by": "perplexity"},
            {"id": "perplexity-research", "name": "Perplexity Research", "owned_by": "perplexity"},
        ]
    
    def get(self, name: str) -> Model:
        """Get a Model by name or alias."""
        key = name.lower().strip()
        if key in self._mapping:
            return self._mapping[key]
        logging.warning(f"Unknown model '{name}', using default")
        return Models.BEST
    
    def list_available(self) -> list[dict[str, str]]:
        """Get list of available models."""
        return self._available
    
    def needs_refresh(self) -> bool:
        """Check if models need refreshing."""
        if not self._last_fetch:
            return True
        return (datetime.now() - self._last_fetch).total_seconds() > self._refresh_interval


# =============================================================================
# Conversation Manager
# =============================================================================

@dataclass
class ConversationSession:
    """Active conversation session."""
    conversation: Conversation
    created_at: datetime
    last_used: datetime
    user_id: str | None = None
    model: str = "perplexity-auto"
    message_count: int = 0


class ConversationManager:
    """Manages persistent conversations with automatic cleanup."""
    
    def __init__(self, client: Perplexity, timeout: int, max_per_user: int):
        self._client = client
        self._timeout = timeout
        self._max_per_user = max_per_user
        self._sessions: Dict[str, ConversationSession] = {}
        self._cleanup_task: asyncio.Task | None = None
    
    def start_cleanup(self) -> None:
        """Start background cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_cleanup(self) -> None:
        """Stop background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _cleanup_loop(self) -> None:
        """Periodically clean up expired sessions."""
        while True:
            await asyncio.sleep(300)
            now = datetime.now()
            expired = [
                cid for cid, sess in self._sessions.items()
                if (now - sess.last_used).total_seconds() > self._timeout
            ]
            for cid in expired:
                del self._sessions[cid]
            if expired:
                logging.info(f"Cleaned up {len(expired)} expired conversations")
    
    def get_or_create(
        self,
        conversation_id: str | None,
        user_id: str | None,
        model: str,
        citation_mode: CitationMode,
    ) -> tuple[str, ConversationSession]:
        """Get existing or create new conversation session."""
        # Return existing
        if conversation_id and conversation_id in self._sessions:
            session = self._sessions[conversation_id]
            session.last_used = datetime.now()
            session.message_count += 1
            return conversation_id, session
        
        # Enforce per-user limit
        if user_id:
            user_sessions = [s for s in self._sessions.values() if s.user_id == user_id]
            if len(user_sessions) >= self._max_per_user:
                oldest = min(user_sessions, key=lambda s: s.last_used)
                for cid, sess in list(self._sessions.items()):
                    if sess is oldest:
                        del self._sessions[cid]
                        break
        
        # Create new
        config = ConversationConfig(citation_mode=citation_mode)
        conversation = self._client.create_conversation(config)
        new_id = conversation_id or str(uuid.uuid4())
        
        session = ConversationSession(
            conversation=conversation,
            created_at=datetime.now(),
            last_used=datetime.now(),
            user_id=user_id,
            model=model,
        )
        self._sessions[new_id] = session
        return new_id, session
    
    def list_sessions(self, user_id: str | None) -> list[dict]:
        """List sessions, optionally filtered by user."""
        result = []
        for cid, sess in self._sessions.items():
            if not user_id or sess.user_id == user_id:
                result.append({
                    "id": cid,
                    "created_at": sess.created_at.isoformat(),
                    "last_used": sess.last_used.isoformat(),
                    "message_count": sess.message_count,
                    "model": sess.model,
                })
        return sorted(result, key=lambda x: x["last_used"], reverse=True)
    
    def delete(self, conversation_id: str, user_id: str | None) -> bool:
        """Delete a conversation session."""
        if conversation_id not in self._sessions:
            return False
        session = self._sessions[conversation_id]
        if user_id and session.user_id and session.user_id != user_id:
            return False
        del self._sessions[conversation_id]
        return True
    
    def get_stats(self) -> dict:
        """Get conversation statistics."""
        return {
            "total": len(self._sessions),
            "users": len(set(s.user_id for s in self._sessions.values() if s.user_id)),
            "messages": sum(s.message_count for s in self._sessions.values()),
        }
    
    def close(self) -> None:
        """Close the Perplexity client."""
        self._client.close()


# =============================================================================
# Pydantic Models
# =============================================================================

class ChatMessage(BaseModel):
    role: str
    content: str
    name: str | None = None


class ChatRequest(BaseModel):
    model: str = "perplexity-auto"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    user: str | None = None
    conversation_id: str | None = None
    citation_mode: str | None = None


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: Usage


class ChunkChoice(BaseModel):
    index: int
    delta: dict[str, Any]
    finish_reason: str | None = None


class ChatChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChunkChoice]


class ModelItem(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[ModelItem]


# =============================================================================
# Global State
# =============================================================================

config: ServerConfig
models: ModelRegistry
manager: ConversationManager
start_time: datetime
request_count: int = 0


# =============================================================================
# Application
# =============================================================================

# Load config early for middleware
config = ServerConfig.from_env()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global models, manager, start_time
    
    start_time = datetime.now()
    
    # Initialize model registry and fetch models
    models = ModelRegistry()
    models.fetch(config.session_token)
    
    # Initialize conversation manager
    client = Perplexity(session_token=config.session_token)
    manager = ConversationManager(client, config.conversation_timeout, config.max_conversations_per_user)
    manager.start_cleanup()
    
    # Setup rate limiting
    if config.enable_rate_limiting:
        limiter = Limiter(key_func=get_remote_address, default_limits=[f"{config.requests_per_minute}/minute"])
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logging.info(f"🚀 Server starting on http://{config.host}:{config.port}")
    logging.info(f"   Models loaded: {len(models._models)}")
    logging.info(f"   Rate limiting: {'Enabled' if config.enable_rate_limiting else 'Disabled'}")
    logging.info(f"   Auth required: {'Yes' if config.api_key else 'No'}")
    
    yield
    
    await manager.stop_cleanup()
    manager.close()


app = FastAPI(
    title="Perplexity OpenAI API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config.enable_rate_limiting:
    app.add_middleware(SlowAPIMiddleware)


# =============================================================================
# Helpers
# =============================================================================

def verify_auth(request: Request) -> str | None:
    """Verify API key and return user ID."""
    if not config.api_key:
        return None
    
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and auth[7:] == config.api_key:
        return hashlib.sha256(auth[7:].encode()).hexdigest()[:16]
    
    raise HTTPException(status_code=401, detail="Invalid API key")


def get_user(request: Request) -> str | None:
    """Get user identifier from request."""
    try:
        return verify_auth(request)
    except HTTPException:
        raise
    except Exception:
        return request.headers.get("X-User-ID")


def messages_to_query(messages: list[ChatMessage]) -> str:
    """Convert messages to query string."""
    user_msgs = [m for m in messages if m.role == "user"]
    sys_msgs = [m for m in messages if m.role == "system"]
    
    if len(user_msgs) == 1 and not sys_msgs:
        return user_msgs[0].content
    
    parts = []
    for msg in messages:
        if msg.role == "system":
            parts.append(f"[System]\n{msg.content}")
        elif msg.role == "user":
            parts.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            parts.append(f"Assistant: {msg.content}")
    return "\n\n".join(parts)


def estimate_tokens(text: str) -> int:
    """Estimate token count."""
    return len(text) // 4


def parse_citation_mode(mode: str | None) -> CitationMode:
    """Parse citation mode string."""
    if not mode:
        return config.default_citation_mode
    try:
        return CitationMode[mode.upper()]
    except KeyError:
        return config.default_citation_mode


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "uptime": (datetime.now() - start_time).total_seconds(),
        "models": len(models._models),
    }


@app.get("/stats")
async def stats(request: Request):
    """Server statistics."""
    get_user(request)
    return {
        "uptime": (datetime.now() - start_time).total_seconds(),
        "requests": request_count,
        "conversations": manager.get_stats(),
        "models": {
            "count": len(models._models),
            "last_refresh": models._last_fetch.isoformat() if models._last_fetch else None,
        },
    }


@app.get("/v1/models", response_model=ModelsResponse)
async def list_models(request: Request):
    """List available models."""
    get_user(request)
    
    if models.needs_refresh():
        models.fetch(config.session_token)
    
    now = int(time.time())
    return ModelsResponse(
        data=[ModelItem(id=m["id"], created=now, owned_by=m["owned_by"]) for m in models.list_available()]
    )


@app.get("/v1/models/{model_id}", response_model=ModelItem)
async def get_model(model_id: str, request: Request):
    """Get model info."""
    get_user(request)
    
    for m in models.list_available():
        if m["id"] == model_id:
            return ModelItem(id=m["id"], created=int(time.time()), owned_by=m["owned_by"])
    
    raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")


@app.post("/v1/models/refresh")
async def refresh_models(request: Request):
    """Force refresh models."""
    get_user(request)
    models.fetch(config.session_token)
    return {"status": "ok", "count": len(models._models)}


@app.get("/conversations")
async def list_conversations(request: Request):
    """List conversations."""
    user_id = get_user(request)
    return {"conversations": manager.list_sessions(user_id)}


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, request: Request):
    """Delete conversation."""
    user_id = get_user(request)
    if manager.delete(conversation_id, user_id):
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatRequest):
    """Chat completions endpoint."""
    global request_count
    request_count += 1
    
    user_id = get_user(request)
    
    if not body.messages:
        raise HTTPException(status_code=400, detail="Messages required")
    
    model_obj = models.get(body.model)
    citation_mode = parse_citation_mode(body.citation_mode)
    
    conv_id, session = manager.get_or_create(
        body.conversation_id, user_id, body.model, citation_mode
    )
    
    query = messages_to_query(body.messages)
    response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    
    try:
        if body.stream:
            return StreamingResponse(
                stream_response(response_id, created, body.model, model_obj, query, session),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Conversation-ID": conv_id},
            )
        else:
            session.conversation.ask(query, model=model_obj, stream=False)
            answer = session.conversation.answer or ""
            
            return ChatResponse(
                id=response_id,
                created=created,
                model=body.model,
                choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=answer))],
                usage=Usage(
                    prompt_tokens=estimate_tokens(query),
                    completion_tokens=estimate_tokens(answer),
                    total_tokens=estimate_tokens(query) + estimate_tokens(answer),
                ),
            )
    except PerplexityError as e:
        logging.error(f"Perplexity error: {e}")
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def stream_response(
    response_id: str,
    created: int,
    model_name: str,
    model: Model,
    query: str,
    session: ConversationSession,
) -> AsyncGenerator[str, None]:
    """Stream chat response."""
    # Initial chunk
    yield f"data: {ChatChunk(id=response_id, created=created, model=model_name, choices=[ChunkChoice(index=0, delta={'role': 'assistant', 'content': ''})]).model_dump_json()}\n\n"
    
    last = ""
    for resp in session.conversation.ask(query, model=model, stream=True):
        current = resp.answer or ""
        if len(current) > len(last):
            delta = current[len(last):]
            last = current
            yield f"data: {ChatChunk(id=response_id, created=created, model=model_name, choices=[ChunkChoice(index=0, delta={'content': delta})]).model_dump_json()}\n\n"
    
    # Final chunk
    yield f"data: {ChatChunk(id=response_id, created=created, model=model_name, choices=[ChunkChoice(index=0, delta={}, finish_reason='stop')]).model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "openai_server:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
    )
