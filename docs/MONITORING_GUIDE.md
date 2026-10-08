# Academic Chatbot - Production Observability & Monitoring Guide

## 1. Monitoring Stack Architecture
The observability stack is composed of three interconnected layers:

```
[ Academic Chatbot App :8501 ] ──(exposes)──> [ Metrics Exporter :8000/metrics ]
                                                      │
                       ┌──────────────────────────────┴──────────────────────────┐
                       ▼                                                         ▼
            [ Prometheus :9090 ]                                         [ Nagios Core ]
             (Scrapes every 5s)                                       (Active Health Checks)
                       │                                                         │
                       ▼                                                         ▼
              [ Grafana :3000 ]                                          [ Alerts / Pager ]
         (Dashboards & Telemetry)                                     (Critical State Alerts)
```

---

## 2. Prometheus Metrics Instrumentation
The application exposes Prometheus metrics over HTTP at `http://localhost:8000/metrics`.

### Key Metrics Catalog:
| Metric Name | Type | Description |
| :--- | :--- | :--- |
| `chatbot_requests_total` | Counter | Total query requests partitioned by `status` (success/error) and `mode` (grounded/standard). |
| `chatbot_query_duration_seconds` | Histogram | Request latency distribution across predefined buckets (0.1s to 30.0s). |
| `chatbot_rag_refusals_total` | Counter | Strict Grounded RAG out-of-domain query refusals. |
| `chatbot_documents_indexed_total` | Gauge | Count of active documents loaded in session. |
| `chatbot_document_chunks_indexed_total` | Gauge | Total vectorized text chunks held in memory. |
| `chatbot_active_sessions` | Gauge | Active user sessions currently connected. |

### Accessing Prometheus Web UI:
Open `http://localhost:9090` in your browser.
* Graph query for P95 latency:
  ```promql
  histogram_quantile(0.95, sum(rate(chatbot_query_duration_seconds_bucket[1m])) by (le))
  ```
* Graph query for query throughput:
  ```promql
  sum(rate(chatbot_requests_total[1m])) by (mode)
  ```

---

## 3. Grafana Telemetry Dashboard
* **URL**: `http://localhost:3000`
* **Default Credentials**: `admin` / `admin`
* **Datasource**: Pre-provisioned to Prometheus (`http://prometheus:9090`)
* **Dashboard UID**: `acad-chatbot-telemetry` ("Academic Chatbot - Production Telemetry & SRE Dashboard")

### Included Panels:
1. **Chatbot Service Status**: Instant status gauge (1 = UP, 0 = DOWN).
2. **Total Processed Queries**: Aggregate throughput counter.
3. **Strict Grounded Refusals**: Real-time counter of out-of-domain prevented hallucinations.
4. **Indexed Knowledge Chunks**: Current document chunk inventory.
5. **RAG Query Latency (P95 vs P50)**: Time-series latency comparison in seconds.
6. **Query Throughput (RPS)**: Request rate broken down by query mode.

---

## 4. Nagios Core Monitoring Plugin
The Nagios plugin (`monitoring/nagios/check_chatbot_health.py`) performs synthetic availability probes.

### Command Line Usage:
```bash
# Check Streamlit app health on port 8501
python monitoring/nagios/check_chatbot_health.py -H localhost -p 8501

# Comprehensive check verifying both app and Prometheus metrics exporter on port 8000
python monitoring/nagios/check_chatbot_health.py -H localhost -p 8501 -m 8000 --check-metrics
```

### Exit Codes:
* `0 - OK`: HTTP 200 received within warning threshold (<1.5s).
* `1 - WARNING`: Latency between 1.5s and 3.0s, or metrics port degraded.
* `2 - CRITICAL`: HTTP 5xx error, connection refused, or latency >3.0s.
* `3 - UNKNOWN`: Invalid command arguments or connection timeout.
