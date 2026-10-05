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

## ⚡ Quick Start

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/SwarajKanse/Academic-Chatbot.git
cd Academic-Chatbot
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

### 3. Run the Assistant
```bash
python -m streamlit run app.py --server.port 8501
```
Or double-click `run.bat` on Windows.
Open `http://localhost:8501` in your browser.
