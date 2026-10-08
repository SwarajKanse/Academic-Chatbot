#!/usr/bin/env python3
"""
Nagios Core Plugin: check_chatbot_health.py
Monitors Academic Chatbot application health and Prometheus metrics exporter.

Exit codes:
  0 - OK: Service is up and responding within acceptable thresholds
  1 - WARNING: Service response time exceeds warning threshold
  2 - CRITICAL: Service is down or returning HTTP errors
  3 - UNKNOWN: Invalid arguments or connection timeout
"""

import sys
import time
import argparse
import urllib.request
import urllib.error

# Nagios Exit Codes
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3


def check_endpoint(url: str, timeout: float) -> tuple[int, float, str]:
    """Sends HTTP GET request, measures latency and status."""
    start_time = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Nagios-Check-AcademicChatbot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = time.time() - start_time
            status_code = response.getcode()
            body = response.read(512).decode("utf-8", errors="ignore")
            return status_code, latency, body
    except urllib.error.HTTPError as e:
        latency = time.time() - start_time
        return e.code, latency, str(e)
    except urllib.error.URLError as e:
        latency = time.time() - start_time
        return -1, latency, str(e.reason)
    except Exception as e:
        latency = time.time() - start_time
        return -2, latency, str(e)


def main():
    parser = argparse.ArgumentParser(description="Nagios Health Check for Academic Chatbot")
    parser.add_argument("-H", "--host", default="localhost", help="Host running Academic Chatbot (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=8501, help="Port for Streamlit app (default: 8501)")
    parser.add_argument("-m", "--metrics-port", type=int, default=8000, help="Port for Prometheus exporter (default: 8000)")
    parser.add_argument("-w", "--warning", type=float, default=1.5, help="Warning threshold in seconds (default: 1.5s)")
    parser.add_argument("-c", "--critical", type=float, default=3.0, help="Critical threshold in seconds (default: 3.0s)")
    parser.add_argument("-t", "--timeout", type=float, default=5.0, help="Connection timeout in seconds (default: 5.0s)")
    parser.add_argument("--check-metrics", action="store_true", help="Also verify Prometheus metrics endpoint")

    args = parser.parse_args()

    app_url = f"http://{args.host}:{args.port}/_stcore/health"
    status_code, latency, body = check_endpoint(app_url, args.timeout)

    # Perfdata string
    perf_data = f"| latency={latency:.4f}s;{args.warning};{args.critical};0;{args.timeout}"

    if status_code == -1 or status_code == -2:
        print(f"CRITICAL - Academic Chatbot connection failed: {body} {perf_data}")
        sys.exit(STATE_CRITICAL)

    if status_code != 200:
        print(f"CRITICAL - Academic Chatbot returned HTTP {status_code} {perf_data}")
        sys.exit(STATE_CRITICAL)

    # If metrics check requested
    if args.check_metrics:
        metrics_url = f"http://{args.host}:{args.metrics_port}/metrics"
        m_status, m_latency, _ = check_endpoint(metrics_url, args.timeout)
        if m_status != 200:
            print(f"WARNING - Academic Chatbot is OK, but Prometheus exporter on port {args.metrics_port} is DOWN {perf_data}")
            sys.exit(STATE_WARNING)

    # Latency thresholds
    if latency >= args.critical:
        print(f"CRITICAL - Academic Chatbot response time {latency:.3f}s exceeds threshold {args.critical}s {perf_data}")
        sys.exit(STATE_CRITICAL)
    elif latency >= args.warning:
        print(f"WARNING - Academic Chatbot response time {latency:.3f}s exceeds threshold {args.warning}s {perf_data}")
        sys.exit(STATE_WARNING)

    print(f"OK - Academic Chatbot is HEALTHY (HTTP {status_code}, response time {latency:.3f}s) {perf_data}")
    sys.exit(STATE_OK)


if __name__ == "__main__":
    main()
