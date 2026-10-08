# ◈ Intelligent Study Assistant: Multi-Tool Conversational RAG

A high-accuracy, zero-hallucination academic assistant built in Python for university engineering, science, and computer science students. Combines in-memory document retrieval (RAG) with autonomous student tools: symbolic mathematics, encyclopedic search, educational lecture finder, and live web research.

---

## 🚀 Key Advantages Over Generic Chatbots

| Capability | Generic Chatbots (ChatGPT / Gemini) | Intelligent Study Assistant |
|---|---|---|
| **Mathematical Precision** | Struggles with complex symbolic calculus & limits | **Exact Symbolic Math** via local SymPy engine |
| **Academic Document RAG** | High hallucination; vague citations | **Exact Page-Level Provenance** (`[Page X]`) + Verbatim citations |
| **Multi-Tool Autonomy** | Relies on generic search or single prompt | **Multi-Turn Autonomous Routing** (Math, Wikipedia, YouTube, Web) |
| **Educational Video Curation** | Generates broken or non-existent URLs | **Direct Verified Lecture Links** (NPTEL, Abdul Bari, MIT OCW) |
| **Privacy & Storage** | Stores chats on cloud servers | **100% In-Memory** vector space wiped on session reset |
| **Study Accelerators** | Requires manual prompt engineering | **One-Click** Summarizer, Practice Quiz & Flashcard Deck Generator |

---

## 🛠️ Integrated Student Tools

1. **SymPy Symbolic Math Engine:** Computes step-by-step integrals ($\int$), derivatives ($\frac{d}{dx}$), limits ($\lim$), matrix operations, and quadratic equations.
2. **Wikipedia Encyclopedia:** Instant lookup of scientific definitions, historical biographies, and theorems.
3. **YouTube Educational Lecture Finder:** Recommends curated video lectures, playlist tutorials, and visual walkthroughs.
4. **Live Academic Web Search:** DuckDuckGo-powered real-time retrieval for exam syllabi, college notices, and academic roadmaps.
5. **In-Memory Academic RAG:** Sublinear TF-IDF + token overlap retrieval tracking exact PDF pages and chapters.

---

## 🎨 UI/UX Design System

* **Modern Floating Input Capsule:** Pinned at bottom center with smooth focus glow.
* **Document-Flow Dialogue:** Conversational flow with right-aligned speech bubbles for user queries and unboxed Markdown/KaTeX for assistant responses.
* **Prompt Scaffolding:** One-click starter cards for rapid exploration.
* **Aesthetic Tokens:** Deep Obsidian canvas (`#121316`), elevated surfaces (`#1f1f23`, `#292a2d`), and Lavender Periwinkle accents (`#c0c1ff`).
* **Typography:** `Space Grotesk` (Headlines), `Inter` (Body Text), `JetBrains Mono` (Badges & Code).

---

## 📦 Project Structure

```
Academic-Chatbot/
├── app.py             # Streamlit UI with floating pill input & KaTeX rendering
├── rag_engine.py      # Multi-tool agentic engine, RAG pipeline & Groq inference
├── requirements.txt   # Python dependencies
├── .env.example       # Template for API keys
├── run.bat            # One-click Windows launcher
└── README.md          # Project documentation
```

---

## 👥 DevOps Engineering Team & Collaboration

This project implements a full production DevOps lifecycle collaboratively developed by:

* **Swaraj Kanse** (`swarajkanse2@gmail.com`) — *Product Owner & Lead AI Architect* (Core RAG Architecture, GitHub Actions CI/CD Pipeline, SCM Management)
* **Adit Mokashi** (`mokashiadit@gmail.com`) — *Scrum Master & DevOps Lead* (Multi-Stage Docker Containerization, Docker Compose Multi-Service Architecture, Jenkins LTS Pipeline)
* **Aryan P** (`aryanpformal@gmail.com`) — *SRE & QA Lead* (Prometheus Metrics Instrumentation, Grafana Telemetry Dashboards, Nagios Core Health Plugins)

---

## 🏗️ DevOps Lifecycle & Operational Architecture

The project implements all 7 core DevOps pillars:

1. **Version Control Operations (Git):**
   * Multi-branch Agile workflow (`feature/**` into `main`) with equal contribution attribution.
   * Automated Git Hooks (`.githooks/pre-commit`, `.githooks/commit-msg`) enforcing Jira ticket format `[ACAD-XXX]` and secret prevention.
   * Annotated release tagging (`v1.0.0`).

2. **Containerization (Docker):**
   * Multi-stage build (`Dockerfile`) compiling cached wheels in `builder` stage and deploying to minimal `python:3.11-slim` runtime.
   * Enforced security: runs as unprivileged user `appuser` (UID 1000).
   * Built-in container healthcheck probing `/_stcore/health`.

3. **Multi-Service Orchestration (Docker Compose):**
   * Orchestrates 4 connected services: `academic-chatbot` (8501/8000), `prometheus` (9090), `grafana` (3000), and `cadvisor` (8080).
   * Isolated bridge network `academic-chatbot-network` and persistent named volumes.

4. **Jenkins Continuous Integration:**
   * Declarative `Jenkinsfile` with 7 stages: SCM Checkout, Static Analysis (Flake8), Pytest with JUnit XML, Docker Build, Container Security Audit, Compose Staging Deploy, and Nagios Verification.
   * Standalone containerized Jenkins LTS stack (`docker-compose.jenkins.yml`) with Docker socket mounting.

5. **Automated Deployment (GitHub Actions):**
   * Workflows in `.github/workflows/ci-cd.yml` and `pr-verify.yml` automated on push, PR, and release tags.
   * Quality gates: Flake8 linting, Pytest test suite, Docker Buildx caching, and live compose smoke tests.

6. **Agile Project Lifecycle (Jira Software Integration):**
   * Jira sprint backlog mapping 4 Sprints, 8 User Stories, acceptance criteria, story points, and assignees (`jira/jira_agile_sprint_lifecycle.json`).
   * Jira CLI helper (`python jira/jira_sync_helper.py --board`) for sprint status and velocity tracking.
   * Smart Commit support: `[ACAD-101] #comment Optimized Docker caching #time 2h #resolve`.

7. **Production Observability (Prometheus, Grafana, Nagios):**
   * **Prometheus:** Exposes application metrics (`/metrics` on port 8000) measuring RPS, P95/P50 latency histograms, and grounded refusal counters.
   * **Grafana:** Pre-provisioned dashboards on `http://localhost:3000` (`admin`/`admin`) with real-time KPI graphs.
   * **Nagios Core:** Standalone synthetic monitoring plugin (`monitoring/nagios/check_chatbot_health.py`) and service definitions (`monitoring/nagios/chatbot_service.cfg`).

---

## ⚡ Deployment & Operation Commands

### Quickstart with Docker Compose:
```bash
# 1. Provide API key
export GROQ_API_KEY="your-api-key"

# 2. Deploy all services in detached mode
docker compose up -d

# 3. Check health with Nagios plugin
python monitoring/nagios/check_chatbot_health.py -H localhost -p 8501 -m 8000 --check-metrics

# 4. View dashboards:
#    Chatbot UI:    http://localhost:8501
#    Prometheus:    http://localhost:9090
#    Grafana:       http://localhost:3000 (admin / admin)
```

### Run Automated Tests:
```bash
pytest tests/ -v
```

### Launch Containerized Jenkins:
```bash
docker compose -f docker-compose.jenkins.yml up -d
# Access Jenkins on http://localhost:8082
```

