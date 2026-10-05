import os
import re
import json
import urllib.parse
from typing import List, Dict, Generator, Tuple, Any
import requests
import pypdf
import sympy as sp
import wikipediaapi
from ddgs import DDGS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WOLFRAM_ALPHA_APPID = os.getenv("WOLFRAM_ALPHA_APPID")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


class DocumentChunk:
    """Represents a text chunk with strict provenance tracking."""
    def __init__(self, text: str, source: str, page: int, chunk_id: int):
        self.text = text.strip()
        self.source = source
        self.page = page
        self.chunk_id = chunk_id

    def to_dict(self):
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "chunk_id": self.chunk_id
        }


# Schema definitions for autonomous model-driven tool calling
STUDENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search the student's uploaded academic document / textbook / lecture notes for relevant sections, definitions, theorems, formulas, and exact page citations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Specific concept, topic, or search terms to retrieve from the uploaded PDF document."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_math",
            "description": "Perform exact mathematical derivations, symbolic calculus (integrals, derivatives, limits), linear algebra, or equation solving using SymPy and Wolfram Alpha.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression_or_problem": {
                        "type": "string",
                        "description": "The mathematical problem or expression (e.g., 'integral of x * exp(x)', 'derivative of sin(x)*cos(x)', 'solve 2*x^2 - 4*x - 6 = 0', 'limit of sin(x)/x as x -> 0')."
                    }
                },
                "required": ["expression_or_problem"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Look up Wikipedia for encyclopedic summaries, foundational scientific concepts, historical context, or biographies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The specific subject or concept title to look up on Wikipedia (e.g. 'Fourier transform', 'Turing machine', 'Claude Shannon')."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_educational_videos",
            "description": "Search YouTube for educational video lectures, course tutorials, or visual walkthroughs on a specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The academic subject or tutorial topic to find videos for (e.g. 'Gilbert Strang Linear Algebra', 'Dijkstra algorithm tutorial')."
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_academic_web",
            "description": "Search the live web for recent university exam details, GATE syllabi, current research updates, documentation, or college curriculum.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for live web retrieval."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


SYSTEM_PROMPT = """You are an Intelligent Academic Study Assistant and Elite Research Tutor.
You assist university students (engineering, computer science, AI & data science, mathematics) and competitive exam aspirants (GATE DA, GATE CS, semester university exams).

CRITICAL DIRECTIVES:
1. BROAD SPECTRUM ASSISTANCE:
   Students can ask questions related to anything:
   - Deep conceptual questions, theory, and code explanations
   - Mathematical derivations, symbolic calculus, and numerical problem solving
   - Academic guidance, syllabus analysis, and exam preparation strategies (GATE, university semesters, placements)
   - Inquiries specific to their uploaded textbooks, research papers, or lecture notes
   - History of science, foundational discoveries, and video lecture recommendations
   NEVER refuse to answer or say 'upload a document' if the question is general or can be answered using your knowledge or tools.

2. AUTONOMOUS TOOL USAGE:
   You have specialized student tools available:
   - `search_document`: Call when the student asks about their uploaded material, textbook contents, or specific pages.
   - `solve_math`: Call when mathematical calculations, symbolic calculus (integrals, derivatives, limits), algebra, or equations need exact computational verification.
   - `search_wikipedia`: Call when an authoritative encyclopedic background or biography is helpful.
   - `find_educational_videos`: Call when the student asks for videos, lecture recommendations, or visual explanations.
   - `search_academic_web`: Call when up-to-date web information, official exam syllabi, or external documentation are needed.
   If no tool is required (e.g. conceptual explanations, general advice, direct reasoning), synthesize the answer directly with highest accuracy.

3. ACCURACY, CITATIONS & STRICT FORMATTING:
   - If document excerpts are retrieved, cite exact page numbers: `[Page X]` or `[Doc, Page X]`.
   - MATHEMATICAL EQUATIONS:
     - ALWAYS format display/block formulas with double dollar signs on their own lines: `$$ <equation> $$`.
     - ALWAYS format inline variables and expressions with single dollar signs: `$ <var> $`.
     - NEVER output `\\[ ... \\]`, `\\( ... \\)`, or raw square brackets around math like `[ \\int ... ]`.
   - ZERO RAW HTML TAGS:
     - NEVER output `<br>`, `<p>`, `<hr>`, or `<div>`.
     - Use clean standard Markdown blank lines for paragraph separation and list formatting.
   - Use clean, elegant Markdown with bold key terms and structured bullet points.
"""


class AcademicRAGEngine:
    """
    Intelligent Multi-Tool Academic Engine.
    Combines In-Memory Document RAG, SymPy & Wolfram Alpha Math,
    Wikipedia Encyclopedia, YouTube Educational Video Search, and Live Web Search.
    """
    def __init__(self, groq_api_key: str = None, model: str = None):
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.chunks: List[DocumentChunk] = []
        self.vectorizer: TfidfVectorizer = None
        self.tfidf_matrix = None
        self.doc_names: List[str] = []
        self.total_pages = 0

    def load_documents(self, uploaded_files) -> Tuple[int, int]:
        """Extracts text, preserves exact page numbers, and builds index."""
        self.chunks.clear()
        self.doc_names.clear()
        self.total_pages = 0
        chunk_counter = 0

        for file in uploaded_files:
            filename = getattr(file, "name", "document.pdf")
            self.doc_names.append(filename)

            try:
                if hasattr(file, "seek"):
                    file.seek(0)
                reader = pypdf.PdfReader(file)
                num_pages = len(reader.pages)
                self.total_pages += num_pages

                for page_idx, page in enumerate(reader.pages):
                    raw_text = page.extract_text() or ""
                    clean_text = self._clean_text(raw_text)
                    if not clean_text:
                        continue

                    # Sliding window (approx 800 chars, 150 overlap)
                    page_chunks = self._chunk_text(clean_text, max_chars=800, overlap=150)
                    for c_text in page_chunks:
                        if len(c_text) > 40:
                            self.chunks.append(DocumentChunk(
                                text=c_text,
                                source=filename,
                                page=page_idx + 1,
                                chunk_id=chunk_counter
                            ))
                            chunk_counter += 1
            except Exception as e:
                print(f"Error parsing {filename}: {e}")

        # Build In-Memory Hybrid TF-IDF Matrix
        if self.chunks:
            texts = [c.text for c in self.chunks]
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words='english',
                sublinear_tf=True,
                max_features=25000
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)

        return len(self.chunks), self.total_pages

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _chunk_text(self, text: str, max_chars: int = 800, overlap: int = 150) -> List[str]:
        sentences = re.split(r'(?<=[.?!])\s+', text)
        chunks = []
        current_chunk = []
        current_len = 0

        for s in sentences:
            s_len = len(s)
            if current_len + s_len > max_chars and current_chunk:
                chunk_str = " ".join(current_chunk)
                chunks.append(chunk_str)
                overlap_text = current_chunk[-1] if current_chunk else ""
                current_chunk = [overlap_text, s] if len(overlap_text) < overlap else [s]
                current_len = sum(len(x) for x in current_chunk)
            else:
                current_chunk.append(s)
                current_len += s_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Hybrid retrieval combining TF-IDF lexical matching and token overlap."""
        if not self.chunks or self.vectorizer is None or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        cos_sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        query_tokens = set(re.findall(r'\b\w{3,}\b', query.lower()))
        scores = []
        for idx, chunk in enumerate(self.chunks):
            cos_score = cos_sims[idx]
            chunk_tokens = set(re.findall(r'\b\w{3,}\b', chunk.text.lower()))
            overlap_ratio = len(query_tokens & chunk_tokens) / max(len(query_tokens), 1)
            final_score = (0.7 * cos_score) + (0.3 * overlap_ratio)
            scores.append((chunk, final_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    # --- TOOLS IMPLEMENTATION ---

    def tool_search_document(self, query: str) -> Tuple[str, List[DocumentChunk]]:
        """Searches uploaded PDFs."""
        if not self.chunks:
            return (
                "Notice: No PDF documents are uploaded in the workspace. Answer the student directly using your general academic knowledge.",
                []
            )

        results = self.retrieve(query, top_k=5)
        if not results:
            return ("No matching sections found in the uploaded document.", [])

        chunks = [r[0] for r in results if r[1] > 0.03]
        if not chunks:
            chunks = [r[0] for r in results[:3]]

        formatted = []
        for c in chunks:
            formatted.append(f"**[Source: {c.source} | Page {c.page}]**\n{c.text}")
        return ("\n\n---\n\n".join(formatted), chunks)

    def tool_solve_math(self, expression_or_problem: str) -> str:
        """Solves math via SymPy and Wolfram Alpha."""
        p_clean = expression_or_problem.strip()
        results = []

        # 1. Wolfram Alpha check (if key configured)
        wolfram_app_id = os.getenv("WOLFRAM_ALPHA_APPID") or WOLFRAM_ALPHA_APPID
        if wolfram_app_id:
            try:
                import wolframalpha
                client = wolframalpha.Client(wolfram_app_id)
                res = client.query(p_clean)
                pods = []
                for pod in getattr(res, "pods", []):
                    for sub in pod.subpods:
                        if sub.plaintext:
                            pods.append(f"**{pod.title}**: {sub.plaintext}")
                if pods:
                    results.append("### Wolfram Alpha Result:\n" + "\n".join(pods[:4]))
            except Exception as e:
                print(f"Wolfram Alpha error: {e}")

        # 2. SymPy Symbolic Solver
        x, y, z, t, n = sp.symbols('x y z t n')
        p_lower = p_clean.lower()
        sympy_output = ""

        try:
            # Integration
            if "integral" in p_lower or "integrate" in p_lower:
                clean_expr = re.sub(r'^(calculate\s+|find\s+|solve\s+)?(the\s+)?(integral|integrate)\s+(of\s+)?', '', p_clean, flags=re.IGNORECASE)
                clean_expr = clean_expr.replace("^", "**").replace("dx", "").strip()
                expr = sp.sympify(clean_expr)
                ans = sp.integrate(expr, x)
                sympy_output = f"**Operation:**\n$$\\int ({sp.latex(expr)})\\,dx$$\n**Exact Result:**\n$${sp.latex(ans)} + C$$"

            # Differentiation
            elif "derivative" in p_lower or "diff" in p_lower or "differentiate" in p_lower:
                clean_expr = re.sub(r'^(calculate\s+|find\s+|solve\s+)?(the\s+)?(derivative\s+of|derivative|diff|differentiate)\s+', '', p_clean, flags=re.IGNORECASE)
                clean_expr = clean_expr.replace("^", "**").strip()
                expr = sp.sympify(clean_expr)
                ans = sp.diff(expr, x)
                sympy_output = f"**Operation:**\n$$\\frac{{d}}{{dx}}({sp.latex(expr)})$$\n**Exact Result:**\n$${sp.latex(ans)}$$"

            # Limit
            elif "limit" in p_lower:
                clean_expr = re.sub(r'^(calculate\s+|find\s+|solve\s+)?(the\s+)?limit\s+(of\s+)?', '', p_clean, flags=re.IGNORECASE)
                point = 0
                if "to" in clean_expr or "->" in clean_expr or "approaches" in clean_expr:
                    parts = re.split(r'to|->|approaches', clean_expr)
                    clean_expr = parts[0].replace("as x", "").strip()
                    try:
                        point = sp.sympify(parts[1].strip())
                    except Exception:
                        point = 0
                expr = sp.sympify(clean_expr.replace("^", "**"))
                ans = sp.limit(expr, x, point)
                sympy_output = f"**Operation:**\n$$\\lim_{{x \\to {point}}} ({sp.latex(expr)})$$\n**Exact Result:**\n$${sp.latex(ans)}$$"

            # Equation Solving
            elif "=" in p_clean or "solve" in p_lower:
                clean_expr = re.sub(r'^(solve\s+for\s+\w+\s*:?|solve\s+)', '', p_clean, flags=re.IGNORECASE)
                if "=" in clean_expr:
                    lhs, rhs = clean_expr.split("=", 1)
                    eq = sp.Eq(sp.sympify(lhs.replace("^", "**")), sp.sympify(rhs.replace("^", "**")))
                else:
                    eq = sp.sympify(clean_expr.replace("^", "**"))
                ans = sp.solve(eq, x)
                sympy_output = f"**Equation:**\n$${sp.latex(eq)}$$\n**Solutions:**\n$${sp.latex(ans)}$$"

            # Simplification / Evaluation
            else:
                expr = sp.sympify(p_clean.replace("^", "**"))
                ans_sym = sp.simplify(expr)
                try:
                    num_val = sp.N(ans_sym, 6)
                    sympy_output = f"**Simplified:**\n$${sp.latex(ans_sym)}$$\n**Numerical Approximation:** {num_val}"
                except Exception:
                    sympy_output = f"**Simplified:**\n$${sp.latex(ans_sym)}$$"

        except Exception as e:
            sympy_output = f"SymPy evaluation note: {str(e)}"

        if sympy_output:
            results.append("### SymPy Symbolic Computation:\n" + sympy_output)

        return "\n\n".join(results) if results else f"Computed: {p_clean}"

    def tool_search_wikipedia(self, topic: str) -> str:
        """Looks up encyclopedic summary."""
        try:
            wiki = wikipediaapi.Wikipedia(
                user_agent="IntelligentStudyAssistant/1.0 (academic-study-assistant)",
                language="en"
            )
            page = wiki.page(topic)
            if page.exists():
                summary = page.summary[:1000]
                return f"**Wikipedia Article: {page.title}**\n\n{summary}...\n\n*Reference:* {page.fullurl}"
            return f"No exact Wikipedia article found for '{topic}'."
        except Exception as e:
            return f"Wikipedia error: {str(e)}"

    def tool_find_educational_videos(self, topic: str) -> str:
        """Finds educational YouTube lectures and tutorials."""
        # 1. Check YouTube API key
        yt_key = os.getenv("YOUTUBE_API_KEY") or YOUTUBE_API_KEY
        if yt_key:
            try:
                url = (
                    f"https://www.googleapis.com/youtube/v3/search?"
                    f"part=snippet&q={urllib.parse.quote(topic)}&key={yt_key}&type=video&maxResults=3"
                )
                resp = requests.get(url, timeout=5).json()
                if resp.get("items"):
                    results = []
                    for item in resp["items"]:
                        vid = item["id"]["videoId"]
                        title = item["snippet"]["title"]
                        channel = item["snippet"]["channelTitle"]
                        results.append(f"- **[{title}](https://www.youtube.com/watch?v={vid})** by *{channel}*")
                    return "\n".join(results)
            except Exception:
                pass

        # 2. Reliable YouTube search extraction fallback
        try:
            q_enc = urllib.parse.quote(topic)
            resp = requests.get(
                f"https://www.youtube.com/results?search_query={q_enc}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5
            )
            vids = list(dict.fromkeys(re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', resp.text)))[:3]
            if vids:
                lines = [f"- 📺 **[Watch Educational Lecture / Tutorial on '{topic}'](https://www.youtube.com/watch?v={v})**" for v in vids]
                lines.append(f"- 🔍 [Explore all YouTube lecture results for '{topic}'](https://www.youtube.com/results?search_query={q_enc})")
                return "\n".join(lines)
        except Exception:
            pass

        q_enc = urllib.parse.quote(topic)
        return f"Explore recommended educational videos: [YouTube Search: {topic}](https://www.youtube.com/results?search_query={q_enc})"

    def tool_search_web(self, query: str) -> str:
        """Searches live web for current syllabus and facts."""
        try:
            results = list(DDGS().text(query, max_results=3))
            if results:
                items = []
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    href = r.get("href", "")
                    items.append(f"**[{title}]({href})**\n{body}")
                return "\n\n".join(items)
            return "No web results found."
        except Exception as e:
            return f"Web search note: {str(e)}"

    def _execute_tool(self, tool_name: str, args: Dict) -> Tuple[str, List[DocumentChunk]]:
        """Dispatches tool call to appropriate handler."""
        chunks = []
        if tool_name == "search_document":
            result_str, chunks = self.tool_search_document(args.get("query", ""))
            return result_str, chunks
        elif tool_name == "solve_math":
            return self.tool_solve_math(args.get("expression_or_problem", "")), []
        elif tool_name == "search_wikipedia":
            return self.tool_search_wikipedia(args.get("topic", "")), []
        elif tool_name == "find_educational_videos":
            return self.tool_find_educational_videos(args.get("topic", "")), []
        elif tool_name == "search_academic_web":
            return self.tool_search_web(args.get("query", "")), []
        return f"Unknown tool: {tool_name}", []

    def generate_answer_stream(
        self, query: str, history: List[Dict] = None
    ) -> Generator[Tuple[Dict[str, Any], List[DocumentChunk]], None, None]:
        """
        Agentic multi-tool response stream.
        Autonomously selects tools or directly synthesizes answers with high accuracy.
        Yields events: {'type': 'tool_start'|'tool_end'|'token', ...}
        """
        if not self.client:
            yield ({"type": "token", "content": "⚠️ **Groq API Key is not configured.** Please check your `.env` file."}, [])
            return

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            for turn in history[-6:]:
                messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": query})

        used_chunks: List[DocumentChunk] = []

        try:
            max_turns = 4
            current_turn = 0

            while current_turn < max_turns:
                current_turn += 1
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=STUDENT_TOOLS,
                    tool_choice="auto",
                    temperature=0.1
                )

                assistant_msg = response.choices[0].message
                tool_calls = assistant_msg.tool_calls

                if tool_calls:
                    messages.append(assistant_msg)
                    for tc in tool_calls:
                        fn_name = tc.function.name
                        try:
                            fn_args = json.loads(tc.function.arguments)
                        except Exception:
                            fn_args = {}

                        yield ({"type": "tool_start", "name": fn_name, "args": fn_args}, used_chunks)

                        tool_result, chunks = self._execute_tool(fn_name, fn_args)
                        if chunks:
                            used_chunks.extend(chunks)

                        yield ({"type": "tool_end", "name": fn_name, "preview": tool_result[:140]}, used_chunks)

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": fn_name,
                            "content": tool_result
                        })
                    # Loop back so model can decide if subsequent tools or final synthesis are needed
                else:
                    # Model has finished tool calls and formulated final response
                    direct_content = assistant_msg.content or ""
                    # Stream tokens in smooth chunks for clean typewriter UI rendering
                    chunk_size = 24
                    for i in range(0, len(direct_content), chunk_size):
                        yield ({"type": "token", "content": direct_content[i:i+chunk_size]}, used_chunks)
                    break

        except Exception as e:
            yield ({"type": "token", "content": f"\n\n**Error querying model:** {str(e)}"}, used_chunks)

    def generate_study_tool(self, tool_type: str) -> str:
        """Generates instant study materials: Summary, Practice Quiz, or Flashcards."""
        if not self.client or not self.chunks:
            return "Please upload documents first in the sidebar to generate study materials."

        sample_size = min(len(self.chunks), 8)
        step = max(1, len(self.chunks) // sample_size)
        sampled_chunks = [self.chunks[i] for i in range(0, len(self.chunks), step)][:sample_size]
        sample_text = "\n\n".join([f"[{c.source}, Page {c.page}]: {c.text}" for c in sampled_chunks])

        prompts = {
            "summary": (
                "Based on the following academic text, generate a high-yield Executive Study Summary.\n"
                "Structure with:\n1. Core Concepts & Definitions\n2. Key Theorems/Formulas/Algorithms\n"
                "3. High-Yield Exam Takeaways with [Page X] citations.\n\n"
                f"Excerpts:\n{sample_text}"
            ),
            "quiz": (
                "Based on the text, create a 5-question exam preparation quiz.\n"
                "Format:\n- 3 Multiple Choice Questions (A, B, C, D with marked Answer & Explanation)\n"
                "- 2 Short Analytical Conceptual Questions with model answers and [Page X] citations.\n\n"
                f"Excerpts:\n{sample_text}"
            ),
            "flashcards": (
                "Extract 6 high-yield Revision Flashcards from this material.\n"
                "Format:\n"
                "### Card [N]: [Concept / Term]\n"
                "- **Core Concept:** ...\n"
                "- **Key Formula / Insight:** ...\n"
                "- **Reference:** [Page X]\n\n"
                f"Excerpts:\n{sample_text}"
            )
        }

        user_prompt = prompts.get(tool_type, prompts["summary"])
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert academic curriculum designer."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        return res.choices[0].message.content
