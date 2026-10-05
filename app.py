import streamlit as st
import os
import sys
import re

# Ensure local module directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from rag_engine import AcademicRAGEngine


def format_academic_markdown(text: str) -> str:
    """
    Cleans HTML tags, normalizes LaTeX math delimiters, and preserves Markdown tables.
    """
    if not text:
        return ""

    # 1. Process line-by-line: preserve <br /> inside tables, convert outside
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if "|" in line:
            # Inside a table row: keep <br /> so the table row is not broken!
            line = re.sub(r"</?br\s*/?>", "<br />", line, flags=re.IGNORECASE)
        else:
            # Outside a table: convert <br> and <p> to standard paragraph breaks
            line = re.sub(r"</?br\s*/?>", "\n\n", line, flags=re.IGNORECASE)
            line = re.sub(r"</?p>", "\n\n", line, flags=re.IGNORECASE)
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    # 2. Clean horizontal rule tags
    text = re.sub(r"</?hr\s*/?>", "\n\n---\n\n", text, flags=re.IGNORECASE)

    # 3. Convert explicit LaTeX display delimiters \[ ... \] to isolated $$ ... $$
    text = re.sub(r"\\\[(.*?)\\\]", lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n", text, flags=re.DOTALL)

    # 4. Convert explicit LaTeX inline delimiters \( ... \) to $ ... $
    text = re.sub(r"\\\((.*?)\\\)", lambda m: f"${m.group(1).strip()}$", text, flags=re.DOTALL)

    # 5. Handle unclosed \[ during active live typing
    if r"\[" in text and r"\]" not in text[text.rfind(r"\["):]:
        text = text + r" \]"
        text = re.sub(r"\\\[(.*?)\\\]", lambda m: f"\n\n$$\n{m.group(1).strip()}\n$$\n\n", text, flags=re.DOTALL)

    # 6. Ensure balanced $$ delimiters
    if text.count("$$") % 2 != 0:
        text += "\n$$\n"

    # 7. Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Page Configuration
st.set_page_config(
    page_title="Intelligent Study Assistant",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Natural & Minimalist Chatbot Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* Color Tokens */
    :root {
        --canvas: #121316;
        --surface-subtle: #1f1f23;
        --surface-elevated: #292a2d;
        --accent-lavender: #c0c1ff;
        --container-iris: #8083ff;
        --on-surface: #e3e2e6;
        --on-surface-variant: #c7c4d7;
        --border-outline: #464554;
        --border-subtle: rgba(255, 255, 255, 0.08);
    }

    /* Overall Layout: Center the conversation column naturally */
    .stApp {
        background-color: var(--canvas) !important;
        color: var(--on-surface) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }

    .main .block-container {
        max-width: 840px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 7.5rem !important;
        margin: 0 auto !important;
    }

    /* Streamlit Chrome Overrides */
    header[data-testid="stHeader"] {
        background-color: var(--canvas) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }
    .stAppDeployButton, #MainMenu, footer {
        display: none !important;
    }

    /* Typography Hierarchy */
    h1, h2, h3, h4, .headline {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--on-surface) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    p, li, .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: var(--on-surface) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        line-height: 1.68 !important;
        font-size: 0.96rem !important;
    }

    /* Protect all Streamlit icons & ligatures from font overrides */
    [data-testid*="stIcon"],
    [data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-icons,
    [data-testid="stFileUploader"] svg {
        font-family: "Material Symbols Rounded", "Source Sans Pro", sans-serif !important;
    }

    code, pre, .mono-badge {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Sleek Sidebar File Uploader Dropzone */
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--surface-subtle) !important;
        border: 1px dashed var(--border-outline) !important;
        border-radius: 12px !important;
        padding: 14px 10px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent-lavender) !important;
        background-color: var(--surface-elevated) !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background-color: var(--surface-elevated) !important;
        color: var(--accent-lavender) !important;
        border: 1px solid var(--border-outline) !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
    }

    /* Top App Bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0 16px 0;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 24px;
    }

    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--on-surface);
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--accent-lavender);
        background: rgba(192, 193, 255, 0.08);
        padding: 2px 7px;
        border-radius: 9999px;
        border: 1px solid rgba(192, 193, 255, 0.2);
    }

    .telemetry-group {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .telemetry-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--on-surface-variant);
        background: var(--surface-subtle);
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid var(--border-subtle);
    }

    .telemetry-pill strong {
        color: var(--accent-lavender);
    }

    /* Welcome Hero (Empty State) */
    .hero-container {
        text-align: center;
        padding: 40px 10px 30px 10px;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--on-surface);
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: var(--on-surface-variant);
        max-width: 540px;
        margin: 0 auto 32px auto;
        line-height: 1.5;
    }

    /* Starter Prompt Cards */
    .prompt-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        text-align: left;
        margin-top: 10px;
    }

    .starter-btn button {
        background-color: var(--surface-subtle) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        text-align: left !important;
        color: var(--on-surface) !important;
        font-size: 0.88rem !important;
        line-height: 1.4 !important;
        transition: all 0.18s ease-in-out !important;
        height: auto !important;
        min-height: 64px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    .starter-btn button:hover {
        background-color: var(--surface-elevated) !important;
        border-color: var(--accent-lavender) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
    }

    /* Clean Modern Chat Message Layout */
    div[data-testid="stChatMessageAvatarUser"],
    div[data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }

    .stChatMessage {
        background-color: transparent !important;
        border: none !important;
        padding: 6px 0 16px 0 !important;
        box-shadow: none !important;
    }

    /* User Message: Elevated, right-aligned clean bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background-color: var(--surface-elevated) !important;
        border: 1px solid var(--border-outline) !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 10px 18px !important;
        max-width: 80% !important;
        margin-left: auto !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25) !important;
    }

    /* Assistant Message: Clean natural document flow without harsh enclosing box */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        display: block !important;
        width: 100% !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        border: none !important;
        padding: 4px 0 16px 0 !important;
        max-width: 100% !important;
    }

    /* Tool Call Pill */
    .tool-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--accent-lavender);
        background: rgba(192, 193, 255, 0.08);
        border: 1px solid rgba(192, 193, 255, 0.25);
        border-radius: 9999px;
        padding: 3px 10px;
        margin-bottom: 12px;
    }

    .tool-pill-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--accent-lavender);
        box-shadow: 0 0 6px var(--accent-lavender);
    }

    /* Verified Source Cards */
    .source-card {
        background: var(--surface-subtle);
        border: 1px solid var(--border-subtle);
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 0.85rem;
        color: var(--on-surface-variant);
        line-height: 1.55;
    }

    .source-card-header {
        display: flex;
        justify-content: space-between;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        color: var(--accent-lavender);
        margin-bottom: 6px;
        font-weight: 600;
    }

    /* Modern Pill Input Bar (ChatGPT / Claude floating style) */
    div[data-testid="stBottom"] {
        background: linear-gradient(180deg, transparent 0%, rgba(18, 19, 22, 0.95) 45%, #121316 100%) !important;
        padding-bottom: 20px !important;
        padding-top: 10px !important;
    }
    div[data-testid="stBottom"] > div {
        max-width: 840px !important;
        margin: 0 auto !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 28px !important;
        border: 1px solid var(--border-outline) !important;
        background-color: var(--surface-subtle) !important;
        box-shadow: 0 10px 36px rgba(0, 0, 0, 0.5) !important;
        padding: 5px 12px !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        max-width: 840px !important;
        margin: 0 auto !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: var(--accent-lavender) !important;
        box-shadow: 0 0 0 2px rgba(192, 193, 255, 0.25), 0 12px 42px rgba(0, 0, 0, 0.65) !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: var(--on-surface) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
        font-size: 0.95rem !important;
    }

    div[data-testid="stChatInput"] button {
        border-radius: 50% !important;
        color: var(--canvas) !important;
        background-color: var(--accent-lavender) !important;
        transition: transform 0.15s ease !important;
    }

    div[data-testid="stChatInput"] button:hover {
        transform: scale(1.06) !important;
        background-color: var(--container-iris) !important;
    }

    /* Beautiful Modern Tables */
    table {
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        margin: 16px 0 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        border: 1px solid var(--border-outline) !important;
        background-color: var(--surface-subtle) !important;
    }
    th {
        background-color: var(--surface-elevated) !important;
        color: var(--accent-lavender) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid var(--border-outline) !important;
        text-align: left !important;
    }
    td {
        padding: 10px 14px !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        color: var(--on-surface) !important;
        font-size: 0.88rem !important;
        line-height: 1.55 !important;
    }
    tr:last-child td {
        border-bottom: none !important;
    }
    tr:hover td {
        background-color: rgba(192, 193, 255, 0.03) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--canvas) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.8rem !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: var(--accent-lavender) !important;
        font-size: 0.88rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .capability-tag {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: var(--on-surface-variant);
        background: var(--surface-subtle);
        border: 1px solid var(--border-subtle);
        border-radius: 6px;
        padding: 3px 8px;
        margin-right: 4px;
        margin-bottom: 6px;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--surface-subtle) !important;
        color: var(--on-surface) !important;
        border: 1px solid var(--border-outline) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 7px 14px !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background-color: var(--surface-elevated) !important;
        border-color: var(--accent-lavender) !important;
        color: var(--accent-lavender) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border-subtle);
        gap: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--on-surface-variant) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 8px 4px !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--accent-lavender) !important;
        border-bottom: 2px solid var(--accent-lavender) !important;
    }

    /* File Uploader */
    div[data-testid="stFileUploader"] {
        background-color: var(--surface-subtle);
        border: 1px dashed var(--border-outline);
        border-radius: 8px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AcademicRAGEngine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

if "stats" not in st.session_state:
    st.session_state.stats = {"chunks": 0, "pages": 0}

if "study_tool_result" not in st.session_state:
    st.session_state.study_tool_result = ""

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

engine = st.session_state.rag_engine

# --- SIDEBAR: Document Library & Tools ---
with st.sidebar:
    st.markdown("### Document Library")
    uploaded_files = st.file_uploader(
        "Drop academic PDFs (textbooks, notes, syllabi)",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        current_names = [f.name for f in uploaded_files]
        if current_names != st.session_state.indexed_files:
            with st.spinner("Indexing documents into in-memory vector space..."):
                num_chunks, num_pages = engine.load_documents(uploaded_files)
                st.session_state.indexed_files = current_names
                st.session_state.stats = {"chunks": num_chunks, "pages": num_pages}
                st.rerun()

    st.markdown("---")
    st.markdown("### Integrated Student Tools")
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span class="capability-tag">◈ SymPy Math Engine</span>
        <span class="capability-tag">◈ Wikipedia Encyclopedia</span>
        <span class="capability-tag">◈ YouTube Lecture Finder</span>
        <span class="capability-tag">◈ Live Academic Web</span>
        <span class="capability-tag">◈ Document RAG</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Study Generators")
    chunks_count = st.session_state.stats["chunks"]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Summary", use_container_width=True, disabled=chunks_count == 0):
            with st.spinner("Generating executive summary..."):
                st.session_state.study_tool_result = engine.generate_study_tool("summary")
                st.toast("Executive Summary ready in Study Lab tab!", icon="📑")
                st.rerun()
    with col2:
        if st.button("Practice Quiz", use_container_width=True, disabled=chunks_count == 0):
            with st.spinner("Generating quiz..."):
                st.session_state.study_tool_result = engine.generate_study_tool("quiz")
                st.toast("Practice Quiz ready in Study Lab tab!", icon="📝")
                st.rerun()

    if st.button("Flashcards Deck", use_container_width=True, disabled=chunks_count == 0):
        with st.spinner("Extracting flashcards..."):
            st.session_state.study_tool_result = engine.generate_study_tool("flashcards")
            st.toast("Flashcards Deck ready in Study Lab tab!", icon="📇")
            st.rerun()

    st.markdown("---")
    if st.button("Reset Chat Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.study_tool_result = ""
        st.session_state.pending_prompt = None
        st.rerun()

# --- MAIN DISPLAY: Minimalist Top Bar ---
chunks_stat = st.session_state.stats["chunks"]
pages_stat = st.session_state.stats["pages"]
clean_model = engine.model.split("/")[-1].upper() if "/" in engine.model else engine.model

st.markdown(f"""
<div class="top-bar">
    <div class="brand-title">
        <span>Study Assistant</span>
        <span class="brand-badge">Multi-Tool RAG</span>
    </div>
    <div class="telemetry-group">
        <span class="telemetry-pill">Model: <strong>{clean_model}</strong></span>
        <span class="telemetry-pill">Pages: <strong>{pages_stat}</strong></span>
        <span class="telemetry-pill">Chunks: <strong>{chunks_stat}</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_chat, tab_study = st.tabs(["Conversation", "Study Lab"])

with tab_study:
    if st.session_state.study_tool_result:
        st.markdown(format_academic_markdown(st.session_state.study_tool_result), unsafe_allow_html=True)
    else:
        st.markdown(
            "<p style='color: var(--on-surface-variant); font-size: 0.92rem;'>"
            "Upload textbooks or lecture notes in the sidebar, then click <strong>Summary</strong>, <strong>Practice Quiz</strong>, or <strong>Flashcards Deck</strong> for automated revision material."
            "</p>",
            unsafe_allow_html=True
        )

with tab_chat:
    # Empty State: Modern Welcome Hero & Starter Prompt Chips
    if not st.session_state.messages:
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">What would you like to explore?</div>
            <div class="hero-subtitle">
                Ask deep technical concepts, step-by-step calculus derivations, university & GATE prep, or upload documents for verified citations.
            </div>
        </div>
        """, unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown('<div class="starter-btn">', unsafe_allow_html=True)
            if st.button("📐 **Derive Quadratic Formula**\n\nStep-by-step completion of square", key="p1", use_container_width=True):
                st.session_state.pending_prompt = "Derive the quadratic formula step by step for ax^2 + bx + c = 0"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="starter-btn">', unsafe_allow_html=True)
            if st.button("📺 **Find Video Lectures on Dijkstra**\n\nTop tutorials & history of invention", key="p2", use_container_width=True):
                st.session_state.pending_prompt = "Find video lectures on Dijkstra algorithm and summarize who invented it"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with sc2:
            st.markdown('<div class="starter-btn">', unsafe_allow_html=True)
            if st.button("🎯 **GATE 2027 Strategy Plan**\n\nBlueprint for TE AI&DS student at TSEC", key="p3", use_container_width=True):
                st.session_state.pending_prompt = "I am a TE AI&DS student at TSEC, how should I plan my preparation for GATE 2027?"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="starter-btn">', unsafe_allow_html=True)
            if st.button("∫ **Solve Symbolic Integral**\n\nIntegrate x * exp(x) with parts derivation", key="p4", use_container_width=True):
                st.session_state.pending_prompt = "Solve the integral of x * exp(x)"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Render Conversation History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("tool_badge"):
                st.markdown(f"""
                <div class="tool-pill">
                    <span class="tool-pill-dot"></span>
                    <span>{msg['tool_badge']}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(format_academic_markdown(msg["content"]), unsafe_allow_html=True)
            if msg.get("sources"):
                with st.expander(f"Verified Citations ({len(msg['sources'])} excerpts)"):
                    for s in msg["sources"]:
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-card-header">
                                <span>{s['source']}</span>
                                <span>PAGE {s['page']}</span>
                            </div>
                            <div>{s['text']}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Determine user prompt (either from input field or clicked starter card)
    user_input = st.chat_input("Ask a question, enter a math formula, or request educational videos...")
    active_prompt = None

    if user_input:
        active_prompt = user_input
    elif st.session_state.pending_prompt:
        active_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if active_prompt:
        st.session_state.messages.append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(format_academic_markdown(active_prompt), unsafe_allow_html=True)

        with st.chat_message("assistant"):
            badge_placeholder = st.empty()
            response_placeholder = st.empty()
            full_response = ""
            used_chunks = []
            active_tools = []

            # Stream answer with autonomous multi-tool execution
            stream = engine.generate_answer_stream(
                query=active_prompt,
                history=st.session_state.messages[:-1]
            )

            tool_labels = {
                "solve_math": "◈ Math Engine (SymPy)",
                "search_document": "◈ Document RAG (Uploaded PDF)",
                "search_wikipedia": "◈ Wikipedia Encyclopedia",
                "find_educational_videos": "◈ YouTube Educational Videos",
                "search_academic_web": "◈ Academic Web Search"
            }

            for event, retrieved_chunks in stream:
                if isinstance(event, dict):
                    event_type = event.get("type")
                    if event_type == "tool_start":
                        t_name = event.get("name", "")
                        label = tool_labels.get(t_name, f"◈ Tool: {t_name}")
                        if label not in active_tools:
                            active_tools.append(label)
                        badge_placeholder.markdown(f"""
                        <div class="tool-pill">
                            <span class="tool-pill-dot"></span>
                            <span>{label}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    elif event_type == "token":
                        token = event.get("content", "")
                        full_response += token
                        response_placeholder.markdown(format_academic_markdown(full_response) + "▌", unsafe_allow_html=True)
                elif isinstance(event, str):
                    full_response += event
                    response_placeholder.markdown(format_academic_markdown(full_response) + "▌", unsafe_allow_html=True)

                if retrieved_chunks:
                    used_chunks = retrieved_chunks

            response_placeholder.markdown(format_academic_markdown(full_response), unsafe_allow_html=True)

            # Verified citations expander if document chunks were referenced
            if used_chunks:
                with st.expander(f"Verified Citations ({len(used_chunks)} excerpts)"):
                    for c in used_chunks:
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-card-header">
                                <span>{c.source}</span>
                                <span>PAGE {c.page}</span>
                            </div>
                            <div>{c.text}</div>
                        </div>
                        """, unsafe_allow_html=True)

            tool_badge_text = " | ".join(active_tools) if active_tools else ""
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "tool_badge": tool_badge_text,
                "sources": [c.to_dict() for c in used_chunks] if used_chunks else []
            })
            st.rerun()
