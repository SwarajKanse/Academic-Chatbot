import pytest
from monitoring.metrics import (
    record_query,
    record_refusal,
    update_document_metrics,
    CHATBOT_REQUESTS_TOTAL,
    CHATBOT_RAG_REFUSALS_TOTAL,
    CHATBOT_DOCUMENTS_INDEXED,
    CHATBOT_DOCUMENT_CHUNKS_INDEXED
)
from monitoring.nagios.check_chatbot_health import check_endpoint, STATE_OK, STATE_CRITICAL


def test_metrics_increment():
    initial_grounded = CHATBOT_REQUESTS_TOTAL.labels(status="success", mode="grounded")._value.get()
    record_query(mode="grounded", duration=0.45, success=True)
    new_grounded = CHATBOT_REQUESTS_TOTAL.labels(status="success", mode="grounded")._value.get()
    assert new_grounded == initial_grounded + 1


def test_refusal_metric():
    initial_refusals = CHATBOT_RAG_REFUSALS_TOTAL.labels(reason="unsupported_in_context")._value.get()
    record_refusal(reason="unsupported_in_context")
    new_refusals = CHATBOT_RAG_REFUSALS_TOTAL.labels(reason="unsupported_in_context")._value.get()
    assert new_refusals == initial_refusals + 1


def test_document_gauges():
    update_document_metrics(doc_count=3, chunk_count=42)
    assert CHATBOT_DOCUMENTS_INDEXED._value.get() == 3
    assert CHATBOT_DOCUMENT_CHUNKS_INDEXED._value.get() == 42


def test_nagios_check_invalid_host():
    status_code, latency, err = check_endpoint("http://127.0.0.1:59999/invalid", timeout=0.5)
    assert status_code < 0  # Should fail to connect
