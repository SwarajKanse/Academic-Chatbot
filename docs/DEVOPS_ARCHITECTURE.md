# Academic Chatbot - DevOps Architecture & Operational Manual

This repository contains the complete DevOps implementation for the **Academic Chatbot & Strict Grounded RAG Platform**, spanning version control, containerization, orchestration, CI/CD automation, Agile sprint lifecycle, and production telemetry.

---

## 1. System Architecture Overview

```
                                      +------------------------------------+
                                      |          GitHub Repository         |
                                      |   github.com/SwarajKanse/...       |
                                      +-----------------+------------------+
                                                        |
                         +------------------------------+------------------------------+
                         | (Webhook / Push Trigger)                                    | (SCM Poll / Webhook)
                         v                                                             v
        +-----------------------------------+                         +-----------------------------------+
        |       GitHub Actions CI/CD        |                         |         Jenkins Pipeline          |
        |  - Flake8 Static Analysis Gate    |                         |  - Environment Sanity Stage       |
        |  - Pytest Suite & Coverage Report |                         |  - Linting & SAST Checks          |
        |  - Multi-Stage Docker Image Build |                         |  - Pytest & JUnit Report Archive  |
        |  - Non-Root Security Verification |                         |  - Multi-Stage Docker Build       |
        |  - Compose Smoke Test & Nagios    |                         |  - Non-Root Container Audit       |
        +-----------------------------------+                         |  - Staging Deployment via Compose |
                                                                      |  - Nagios Health Verification     |
                                                                      +-----------------+-----------------+
                                                                                        |
                                                                                        v
                                                           +-----------------------------------------------+
                                                           |           Docker Compose Multi-Service        |
                                                           |                                               |
                                                           |   +-------------------+  (Port 8501 / 8000)   |
                                                           |   | academic-chatbot  | <--- User / Students  |
                                                           |   +---------+---------+                       |
                                                           |             |                                 |
                                                           |             v (Port 8000 /metrics)            |
                                                           |   +---------+---------+                       |
                                                           |   |    prometheus     | (Port 9090)           |
                                                           |   +---------+---------+                       |
                                                           |             |                                 |
                                                           |             v                                 |
                                                           |   +---------+---------+                       |
                                                           |   |      grafana      | (Port 3000)           |
                                                           |   +-------------------+                       |
                                                           +-----------------------------------------------+
```

---

## 2. Seven DevOps Pillars Implemented

### Pillar 1: Version Control Operations using Git
* **Distributed Collaborative Development**: Feature branching model with commits balanced equally across:
  * `Swaraj Kanse <swarajkanse2@gmail.com>`
  * `Adit Mokashi <mokashiadit@gmail.com>`
  * `Aryan P <aryanpformal@gmail.com>`
* **Conventional Commits & Jira Smart Tags**: Formatted as `[ACAD-XXX] feat: description`
* **Automated Git Hooks**:
  * `.githooks/pre-commit`: Scans for leaked credentials/secrets before commit.
  * `.githooks/commit-msg`: Enforces Jira ticket keys on every commit.

### Pillar 2: Containerize Application using Docker
* **Multi-Stage Build** (`Dockerfile`):
  * **Stage 1 (`builder`)**: Compiles binary dependencies and caches wheels in `/build/wheels`.
  * **Stage 2 (`runner`)**: Unprivileged runtime container using `python:3.11-slim`, running under user `appuser` (UID 1000).
* **Security & Footprint Optimization**: Excludes unwanted artifacts via `.dockerignore`.
* **Healthcheck**: Embedded OCI container healthcheck polling `/_stcore/health`.

### Pillar 3: Multi-Service Orchestration using Docker Compose
* **Orchestration File**: `docker-compose.yml`
* **Services**:
  1. `academic-chatbot`: Streamlit RAG application (`8501`) and Prometheus metrics server (`8000`).
  2. `prometheus`: Scrapes application and container performance metrics (`9090`).
  3. `grafana`: Pre-provisioned dashboards and datasources (`3000`).
  4. `cadvisor`: Real-time hardware and container metrics exporter (`8080`).
* **Isolated Network**: Custom bridge network `academic-chatbot-network`.
* **Data Persistence**: Named volumes for Prometheus TSDB and Grafana configurations.

### Pillar 4: Jenkins CI/CD Pipeline
* **Pipeline Definition**: Declarative `Jenkinsfile` with 7 stages:
  1. `SCM Checkout & Environment Sanity`
  2. `Static Code Analysis & Linting`
  3. `Automated Unit & Integration Tests`
  4. `Docker Container Build & Tagging`
  5. `Container Security & Health Audit`
  6. `Deploy Multi-Service Application`
  7. `Smoke Test & Nagios Health Verification`
* **Containerized Jenkins LTS**: Standalone deployment via `docker compose -f docker-compose.jenkins.yml up -d` on port `8082`.

### Pillar 5: Automated Deployment via GitHub Actions
* **Workflow**: `.github/workflows/ci-cd.yml`
* **Gates**: Triggers automatically on `push` and `pull_request` to `main` and version tags `v*`.
* **Execution**: Automated linting, test suite execution, Docker Buildx caching, and smoke testing.

### Pillar 6: Agile Project Lifecycle with Jira Integration
* **Specification File**: `jira/jira_agile_sprint_lifecycle.json`
* **Agile Documentation**: `docs/AGILE_JIRA_SPRINT_LIFECYCLE.md`
* **CLI Management**: `python jira/jira_sync_helper.py --board`
* **Sprints**: 4 completed/active sprints mapping 8 user stories with acceptance criteria and story points.

### Pillar 7: Monitoring & Observability (Prometheus, Grafana, Nagios)
* **Prometheus**: Real-time metrics scraper on `http://localhost:9090` with alerting rules (`monitoring/prometheus/alert.rules.yml`).
* **Grafana**: Interactive dashboards on `http://localhost:3000` (`admin`/`admin`) visualizing P95 latency, RPS, and Grounded RAG refusals.
* **Nagios**: Synthetic monitor plugin (`monitoring/nagios/check_chatbot_health.py`) and service definitions (`monitoring/nagios/chatbot_service.cfg`).

---

## 3. Quickstart & Deployment Commands

### Running Locally with Docker Compose:
```bash
# 1. Set environment variables
export GROQ_API_KEY="your-api-key"

# 2. Start the full multi-service stack in detached mode
docker compose up -d

# 3. Verify container health
docker compose ps
python monitoring/nagios/check_chatbot_health.py -H localhost -p 8501 -m 8000 --check-metrics

# 4. Access services:
#    - Chatbot Web UI:    http://localhost:8501
#    - Prometheus Web:    http://localhost:9090
#    - Grafana Dashboard: http://localhost:3000
```

### Running Containerized Jenkins:
```bash
docker compose -f docker-compose.jenkins.yml up -d
# Access Jenkins on http://localhost:8082
```

### Running Tests:
```bash
pytest tests/ -v
```
