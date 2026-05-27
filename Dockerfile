FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY openai_server.py ./

# Install Python dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install . fastapi uvicorn[standard] python-dotenv slowapi python-multipart

# Adjust ownership
RUN chown -R app:app /app

USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Run the server
CMD ["uvicorn", "openai_server:app", "--host", "0.0.0.0", "--port", "8000"]
