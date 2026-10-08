import os
import sys
import subprocess
from monitoring.metrics import start_metrics_server


def main():
    # 1. Initialize Prometheus HTTP metrics exporter immediately on container boot
    metrics_port = int(os.getenv("METRICS_PORT", 8000))
    start_metrics_server(port=metrics_port)
    print(f"[Academic-Chatbot-Bootstrap] Prometheus metrics exporter active on port {metrics_port}")

    # 2. Launch Streamlit application server
    app_port = os.getenv("STREAMLIT_SERVER_PORT", "8501")
    app_addr = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    cmd = [
        "streamlit", "run", "app.py",
        f"--server.port={app_port}",
        f"--server.address={app_addr}",
        "--server.headless=true"
    ]
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
