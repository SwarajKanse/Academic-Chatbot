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




TOOL_LABELS = {
    "solve_math": "Math engine",
    "search_document": "Your documents",
    "search_wikipedia": "Wikipedia",
    "find_educational_videos": "YouTube",
    "search_academic_web": "Web search",
}

SUGGESTIONS = [
    "Derive the quadratic formula step by step",
    "Integrate x * exp(x)",
    "Explain Dijkstra's algorithm and find a good lecture on it",
    "How should I plan my GATE preparation?",
]

st.set_page_config(page_title="Study Assistant", layout="centered")

# Light touch on top of the theme in .streamlit/config.toml
st.markdown("""
<style>
    #MainMenu, footer, .stAppDeployButton { display: none; }
    .block-container { padding-top: 3rem; padding-bottom: 6rem; }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] { display: none; }
    [data-testid="stChatMessage"] { padding: 0.25rem 0; background: transparent; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        background: var(--st-secondary-background-color, #f1efe9);
        border-radius: 10px;
        padding: 0.6rem 0.9rem;
    }
    h1 { font-size: 2.1rem !important; }
    [data-testid="stBaseButton-tertiary"] { color: #2f5d50; }
    [data-testid="stBaseButton-tertiary"]:hover { text-decoration: underline; }
    .tools-used { font-size: 0.8rem; color: #8a867c; margin-bottom: 0.25rem; }
</style>
""", unsafe_allow_html=True)


def tools_line(labels):
    if labels:
        st.markdown(f'<div class="tools-used">Used: {" · ".join(labels)}</div>', unsafe_allow_html=True)


def show_sources(sources):
    """sources: list of dicts with source, page, text."""
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})"):
        for s in sources:
            st.markdown(f"**{s['source']}**, page {s['page']}")
            st.caption(s["text"])


# Session state
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = AcademicRAGEngine()
st.session_state.setdefault("messages", [])
st.session_state.setdefault("indexed_files", [])
st.session_state.setdefault("pending_prompt", None)

engine = st.session_state.rag_engine
has_docs = bool(st.session_state.indexed_files)

# Sidebar
with st.sidebar:
    st.subheader("Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs to ask questions about them",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        current_names = [f.name for f in uploaded_files]
        if current_names != st.session_state.indexed_files:
            with st.spinner("Reading documents..."):
                engine.load_documents(uploaded_files)
            st.session_state.indexed_files = current_names
            st.rerun()

    if has_docs:
        st.subheader("Study tools")
        for label, kind in [("Summary", "summary"), ("Quiz", "quiz"), ("Flashcards", "flashcards")]:
            if st.button(label, use_container_width=True):
                with st.spinner(f"Making {label.lower()}..."):
                    result = engine.generate_study_tool(kind)
                st.session_state.messages.append({"role": "user", "content": f"{label} of my documents"})
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.rerun()

    st.divider()
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

# Main
st.title("Study Assistant")

if not st.session_state.messages:
    st.write("Ask about a concept, work through a problem, or upload your notes in the sidebar.")
    st.caption("Try one of these")
    for i, s in enumerate(SUGGESTIONS):
        if st.button(f"→ {s}", key=f"suggest{i}", type="tertiary"):
            st.session_state.pending_prompt = s
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tools"):
            tools_line(msg["tools"])
        st.markdown(format_academic_markdown(msg["content"]), unsafe_allow_html=True)
        show_sources(msg.get("sources"))

user_input = st.chat_input("Ask a question")
prompt = user_input or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(format_academic_markdown(prompt), unsafe_allow_html=True)

    with st.chat_message("assistant"):
        tools_slot = st.empty()
        answer_slot = st.empty()
        answer = ""
        used_chunks = []
        tools = []

        stream = engine.generate_answer_stream(query=prompt, history=st.session_state.messages[:-1])
        for event, retrieved_chunks in stream:
            if isinstance(event, dict):
                if event.get("type") == "tool_start":
                    label = TOOL_LABELS.get(event.get("name", ""), event.get("name", ""))
                    if label and label not in tools:
                        tools.append(label)
                    with tools_slot.container():
                        tools_line(tools)
                elif event.get("type") == "token":
                    answer += event.get("content", "")
                    answer_slot.markdown(format_academic_markdown(answer) + " ▍", unsafe_allow_html=True)
            elif isinstance(event, str):
                answer += event
                answer_slot.markdown(format_academic_markdown(answer) + " ▍", unsafe_allow_html=True)
            if retrieved_chunks:
                used_chunks = retrieved_chunks

        answer_slot.markdown(format_academic_markdown(answer), unsafe_allow_html=True)
        sources = [c.to_dict() for c in used_chunks]
        show_sources(sources)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "tools": tools,
        "sources": sources,
    })
    st.rerun()
