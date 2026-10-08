# Multi-Stage Production Dockerfile for Academic Chatbot
# ==============================================================================
# Stage 1: Build stage (compile wheels and cache dependencies)
# ==============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Pre-compile wheels using PyPI pre-built binaries
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ==============================================================================
# Stage 2: Runtime Production Image
# ==============================================================================
FROM python:3.11-slim AS runner

# Label metadata for OCI compliance
LABEL org.opencontainers.image.title="Academic Chatbot" \
      org.opencontainers.image.description="AI-driven Academic Research Assistant & Strict Grounded RAG Platform" \
      org.opencontainers.image.authors="Swaraj Kanse <swarajkanse2@gmail.com>, Adit Mokashi <mokashiadit@gmail.com>, Aryan P <aryanpformal@gmail.com>" \
      org.opencontainers.image.source="https://github.com/SwarajKanse/Academic-Chatbot" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    METRICS_PORT=8000

# Install runtime utilities (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged application user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

WORKDIR /app

# Copy wheels from builder stage and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application source code
COPY --chown=appuser:appgroup app.py rag_engine.py ./
COPY --chown=appuser:appgroup .streamlit/ .streamlit/
COPY --chown=appuser:appgroup monitoring/ monitoring/

# Switch to unprivileged user
USER appuser

# Expose Streamlit UI port (8501) and Prometheus metrics exporter port (8000)
EXPOSE 8501 8000

# Standard OCI Healthcheck
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Launch application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
