# Agile Software Project Lifecycle & Jira DevOps Integration

## 1. Project Overview & Governance
* **Project Key**: `ACAD`
* **Project Name**: Academic Chatbot Platform & RAG Engine
* **Methodology**: Agile Scrum with Continuous Delivery
* **Sprint Duration**: 2-week iterations
* **Tooling Stack**: Atlassian Jira Software, GitHub Actions, Jenkins LTS, Docker, Prometheus, Grafana

---

## 2. Team Composition & Resource Allocation
All three team members contribute equally across engineering domains:

| Team Member | Email Address | Agile Role | Primary Responsibilities |
| :--- | :--- | :--- | :--- |
| **Swaraj Kanse** | `swarajkanse2@gmail.com` | Product Owner & Lead AI Architect | Core RAG Architecture, Grounded Semantic Retrieval, GitHub Actions CI/CD Pipeline |
| **Adit Mokashi** | `mokashiadit@gmail.com` | Scrum Master & DevOps Lead | Multi-Stage Containerization, Docker Compose Multi-Service Architecture, Jenkins LTS Pipeline |
| **Aryan P** | `aryanpformal@gmail.com` | SRE & Quality Assurance Lead | Prometheus Observability Exporter, Grafana Telemetry Dashboards, Nagios Health Plugins |

---

## 3. Sprint Roadmap & Milestone Tracking

### Sprint 1: Grounded RAG Foundation (Closed)
* **Goal**: Establish the core vector search engine and strict grounding constraints.
* **Velocity Delivered**: 21 Story Points.
* **Key Deliverables**: Hybrid TF-IDF indexer, PDF page provenance tracker, out-of-domain refusal guardrails.

### Sprint 2: Academic UI & Formula Formatting (Closed)
* **Goal**: Modernize web interface with mathematical LaTeX rendering and interactive tools.
* **Velocity Delivered**: 18 Story Points.
* **Key Deliverables**: Editorial light theme, multi-line equation parser, flashcard & summary generators.

### Sprint 3: Containerization & Automation Pipelines (Active)
* **Goal**: Full Dockerization, Jenkins declarative pipeline, and GitHub Actions CI/CD.
* **Target Velocity**: 26 Story Points.
* **Key Deliverables**: Production multi-stage `Dockerfile`, multi-service `docker-compose.yml`, `Jenkinsfile`, `.github/workflows/ci-cd.yml`.

### Sprint 4: Production Observability & SRE Stack (Active)
* **Goal**: End-to-end monitoring with Prometheus metrics, Grafana dashboards, and Nagios alerting.
* **Target Velocity**: 21 Story Points.
* **Key Deliverables**: `monitoring/metrics.py`, Prometheus scraper configs, Grafana dashboard JSON, Nagios `check_chatbot_health.py` plugin.

---

## 4. Jira User Story Backlog

### Epic ACAD-EPIC-3: Containerization & Infrastructure
* **[ACAD-101]** Implement Multi-Stage Dockerfile with Non-Root Security User
  * **Assignee**: Adit Mokashi (`mokashiadit@gmail.com`)
  * **Points**: 5 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * Given Python dependencies in `requirements.txt`, when building the image, then wheels are compiled in builder stage.
    * Given runtime container execution, then process runs as UID 1000 (`appuser`).
    * Built-in `HEALTHCHECK` verifies `/_stcore/health` every 20 seconds.
* **[ACAD-102]** Orchestrate Multi-Service Architecture with Docker Compose
  * **Assignee**: Adit Mokashi (`mokashiadit@gmail.com`)
  * **Points**: 5 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * Compose file links `academic-chatbot`, `prometheus`, `grafana`, and `cadvisor`.
    * Prometheus scrapes metrics on internal bridge network `academic-chatbot-network`.
    * Persistent volumes retain Prometheus TSDB and Grafana dashboards.

### Epic ACAD-EPIC-4: Continuous Integration & Deployment (CI/CD)
* **[ACAD-103]** Configure Containerized Jenkins LTS Pipeline with Declarative Jenkinsfile
  * **Assignee**: Swaraj Kanse (`swarajkanse2@gmail.com`)
  * **Points**: 8 | **Priority**: Highest | **Status**: Done
  * **Acceptance Criteria**:
    * 7 distinct pipeline stages: Checkout, Lint, Unit Test, Docker Build, Security Audit, Compose Deploy, Nagios Verification.
    * Automated JUnit test report archiving.
* **[ACAD-104]** Automate GitHub Actions CI/CD Pipeline
  * **Assignee**: Swaraj Kanse (`swarajkanse2@gmail.com`)
  * **Points**: 5 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * Workflow triggers on pushes to `main`, `feature/**`, and tag releases `v*`.
    * Flake8 linting and Pytest unit test suites pass prior to Docker image build.
* **[ACAD-108]** Enforce Jira Smart Commit Git Hooks and Conventional Commits
  * **Assignee**: Swaraj Kanse (`swarajkanse2@gmail.com`)
  * **Points**: 3 | **Priority**: Medium | **Status**: Done
  * **Acceptance Criteria**:
    * Pre-commit and commit-msg hooks validate `[ACAD-XXX]` issue format.

### Epic ACAD-EPIC-5: Production Observability & SRE Stack
* **[ACAD-105]** Instrument Python Application with Prometheus Metrics Exporter
  * **Assignee**: Aryan P (`aryanpformal@gmail.com`)
  * **Points**: 5 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * Expose `/metrics` endpoint on port 8000.
    * Track query duration histogram, total requests counter, grounded refusals, and active indexed chunks.
* **[ACAD-106]** Design Production Grafana Dashboard with Real-Time SRE Telemetry
  * **Assignee**: Aryan P (`aryanpformal@gmail.com`)
  * **Points**: 5 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * Automated provisioning of Prometheus datasource and telemetry dashboard.
    * Visualizations for P95/P50 latency percentiles, throughput RPS, and grounded refusal ratios.
* **[ACAD-107]** Develop Nagios Core Monitoring Plugin and Service Definitions
  * **Assignee**: Aryan P (`aryanpformal@gmail.com`)
  * **Points**: 3 | **Priority**: High | **Status**: Done
  * **Acceptance Criteria**:
    * `check_chatbot_health.py` conforms to Nagios plugin API (Exit 0=OK, 1=WARN, 2=CRIT, 3=UNKNOWN).
    * Outputs performance data metrics (`| latency=0.042s;1.5;3.0;0;5.0`).

---

## 5. Jira Smart Commits Workflow
Team members link code changes directly to Jira issues using the Smart Commit syntax:

```bash
git commit -m "[ACAD-101] #comment Optimized multi-stage Docker build #time 2h #resolve"
git commit -m "[ACAD-105] #comment Added Prometheus metrics exporter on port 8000 #time 3h"
```

## 6. CLI Management Helper
Run the local CLI sync tool to inspect the board status:
```bash
python jira/jira_sync_helper.py --board
python jira/jira_sync_helper.py --summary
```
