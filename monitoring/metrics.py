"""
Academic Chatbot - Prometheus Metrics Instrumentation
Provides real-time application metrics, latency tracking, and operational observability.
"""

import os
import time
import logging
from typing import Optional
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    start_http_server,
    REGISTRY
)

logger = logging.getLogger("academic_chatbot_metrics")

# Application & Business Metrics
CHATBOT_REQUESTS_TOTAL = Counter(
    "chatbot_requests_total",
    "Total incoming user query requests processed by the chatbot",
    ["status", "mode"]  # status: success, error; mode: grounded, fallback, general
)

CHATBOT_QUERY_DURATION_SECONDS = Histogram(
    "chatbot_query_duration_seconds",
    "Time taken to synthesize answers and execute RAG pipelines",
    ["mode"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0]
)

CHATBOT_RAG_REFUSALS_TOTAL = Counter(
    "chatbot_rag_refusals_total",
    "Total queries strictly refused due to lack of document grounding",
    ["reason"]
)

CHATBOT_DOCUMENTS_INDEXED = Gauge(
    "chatbot_documents_indexed_total",
    "Number of active documents indexed in current session"
)

CHATBOT_DOCUMENT_CHUNKS_INDEXED = Gauge(
    "chatbot_document_chunks_indexed_total",
    "Number of vector chunks currently in memory"
)

CHATBOT_ACTIVE_USERS = Gauge(
    "chatbot_active_sessions",
    "Number of active user sessions currently interacting with the application"
)

# Server singleton state
_SERVER_STARTED = False


def start_metrics_server(port: int = 8000) -> bool:
    """
    Starts the Prometheus metrics HTTP exporter on the specified port.
    Safe to call multiple times (idempotent).
    """
    global _SERVER_STARTED
    if _SERVER_STARTED:
        return True

    metrics_port = int(os.getenv("METRICS_PORT", port))
    try:
        start_http_server(metrics_port)
        _SERVER_STARTED = True
        logger.info(f"Prometheus metrics exporter started on port {metrics_port}")
        return True
    except OSError as e:
        # Port already in use (e.g. during Streamlit auto-reloads)
        logger.warning(f"Metrics server already running or port {metrics_port} occupied: {e}")
        _SERVER_STARTED = True
        return True
    except Exception as e:
        logger.error(f"Failed to start Prometheus metrics server: {e}")
        return False


def record_query(mode: str, duration: float, success: bool = True):
    """Record query throughput and latency metrics."""
    status = "success" if success else "error"
    CHATBOT_REQUESTS_TOTAL.labels(status=status, mode=mode).inc()
    CHATBOT_QUERY_DURATION_SECONDS.labels(mode=mode).observe(duration)


def record_refusal(reason: str = "out_of_domain"):
    """Record a strict grounding refusal."""
    CHATBOT_RAG_REFUSALS_TOTAL.labels(reason=reason).inc()


def update_document_metrics(doc_count: int, chunk_count: int):
    """Update active document and chunk gauges."""
    CHATBOT_DOCUMENTS_INDEXED.set(doc_count)
    CHATBOT_DOCUMENT_CHUNKS_INDEXED.set(chunk_count)
