"""
AI Coding Assistant - Streamlit Frontend
Dark-themed, VS Code-inspired 3-panel layout.
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path

# ─── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="AI Coding Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global theme ── */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg-primary:   #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary:  #0d1b2e;
        --accent:       #3b82f6;
        --accent-dim:   #1d4ed8;
        --success:      #22c55e;
        --warning:      #f59e0b;
        --danger:       #ef4444;
        --text-primary: #e2e8f0;
        --text-muted:   #64748b;
        --border:       #1e293b;
        --code-bg:      #111827;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--bg-tertiary) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* Main content */
    .main .block-container {
        padding: 1rem 1.5rem;
        max-width: 100%;
        background-color: var(--bg-primary);
    }

    /* Buttons */
    .stButton > button {
        background: var(--accent) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.4rem 1rem !important;
        transition: background 0.2s ease !important;
    }
    .stButton > button:hover {
        background: var(--accent-dim) !important;
    }

    /* Text areas */
    .stTextArea textarea, .stTextInput input {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }

    /* Select boxes */
    .stSelectbox select, [data-baseweb="select"] {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }

    /* Chat messages */
    .chat-message {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.6;
    }
    .chat-user {
        background: var(--bg-secondary);
        border-left: 3px solid var(--accent);
    }
    .chat-assistant {
        background: #0d1b2e;
        border-left: 3px solid var(--success);
    }
    .chat-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        text-transform: uppercase;
    }
    .label-user   { color: var(--accent); }
    .label-bot    { color: var(--success); }

    /* Code blocks */
    .code-block {
        background: var(--code-bg);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        overflow-x: auto;
        white-space: pre-wrap;
        margin: 8px 0;
    }

    /* Panel header */
    .panel-header {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 12px;
    }

    /* Intent badge */
    .intent-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .intent-debug    { background: #450a0a; color: #fca5a5; }
    .intent-explain  { background: #0c1a3b; color: #93c5fd; }
    .intent-generate { background: #052e16; color: #86efac; }
    .intent-refactor { background: #1c1003; color: #fde68a; }
    .intent-test     { background: #1a0a2e; color: #c4b5fd; }
    .intent-optimize { background: #0a1a2e; color: #67e8f9; }
    .intent-query    { background: #1e293b; color: #94a3b8; }

    /* File tree */
    .file-item {
        padding: 4px 8px;
        border-radius: 4px;
        cursor: pointer;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: var(--text-primary);
    }
    .file-item:hover { background: var(--bg-secondary); }

    /* Diff view */
    .diff-original { background: #1a0000; border-left: 3px solid var(--danger); }
    .diff-fixed    { background: #001a00; border-left: 3px solid var(--success); }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent) !important;
    }

    /* Status bar */
    .status-bar {
        background: var(--accent);
        color: #fff;
        padding: 2px 12px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        border-radius: 4px;
        display: inline-block;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── Session state initialisation ─────────────────────────────────────────────
def init_session():
    defaults = {
        "chat_history": [],       # [{user, assistant, intent, code_blocks}]
        "memory": [],             # [{user, assistant}] for LLM memory
        "selected_file": None,
        "selected_file_content": "",
        "project_dir": "",
        "project_loaded": False,
        "active_tab": "Chat",
        "last_response": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── API helpers ──────────────────────────────────────────────────────────────
def api_post(endpoint: str, payload: dict) -> dict | None:
    try:
        r = requests.post(f"{BACKEND_URL}/{endpoint}", json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend. Is FastAPI running on port 8000?")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def intent_badge(intent: str) -> str:
    return f'<span class="intent-badge intent-{intent}">{intent}</span>'


def render_chat_message(turn: dict):
    """Render a single chat turn with user + assistant messages."""
    # User message
    st.markdown(
        f'<div class="chat-message chat-user">'
        f'<div class="chat-label label-user">You</div>'
        f'{turn["user"]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Assistant message
    badge = intent_badge(turn.get("intent", "query"))
    st.markdown(
        f'<div class="chat-message chat-assistant">'
        f'<div class="chat-label label-bot">Assistant {badge}</div>'
        f'{turn["assistant"]}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Code action buttons for each extracted code block
    for i, block in enumerate(turn.get("code_blocks", [])):
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(f"📋 Copy Block {i+1}", key=f"copy_{id(turn)}_{i}"):
                st.code(block, language="python")
        with col2:
            if st.button(f"✏️ Load to Editor {i+1}", key=f"load_{id(turn)}_{i}"):
                st.session_state.selected_file_content = block
                st.session_state.selected_file = "from_ai.py"


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="panel-header">🤖 AI Coding Assistant</div>', unsafe_allow_html=True)

    # ── Project loader
    st.markdown("**📁 Load Project**")
    project_path = st.text_input(
        "Project directory path",
        value=st.session_state.project_dir,
        placeholder="/path/to/your/project",
        label_visibility="collapsed",
    )

    if st.button("🚀 Ingest Codebase", use_container_width=True):
        if project_path:
            with st.spinner("Ingesting codebase..."):
                result = api_post("upload_codebase", {"project_dir": project_path})
            if result and result.get("status") == "success":
                st.session_state.project_dir = project_path
                st.session_state.project_loaded = True
                st.success(
                    f"✅ Loaded {result['files_processed']} files, "
                    f"{result['chunks_stored']} chunks"
                )
            elif result:
                st.error(result.get("message", "Ingestion failed"))
        else:
            st.warning("Enter a project directory path")

    st.divider()

    # ── File explorer (simple manual path loader)
    st.markdown("**🗂 File Explorer**")
    manual_file = st.text_input(
        "Open file path",
        placeholder="/path/to/file.py",
        label_visibility="collapsed",
    )
    if st.button("📄 Open File", use_container_width=True):
        if manual_file and Path(manual_file).exists():
            try:
                content = Path(manual_file).read_text(encoding="utf-8", errors="ignore")
                st.session_state.selected_file = Path(manual_file).name
                st.session_state.selected_file_content = content
                st.success(f"Opened: {Path(manual_file).name}")
            except Exception as e:
                st.error(f"Could not read file: {e}")
        else:
            st.warning("File not found")

    st.divider()

    # ── Feature buttons
    st.markdown("**⚡ Quick Actions**")

    if st.button("🐛 Debug Code", use_container_width=True):
        st.session_state.active_tab = "Debug"
    if st.button("✨ Generate Code", use_container_width=True):
        st.session_state.active_tab = "Generate"
    if st.button("🔧 Refactor Code", use_container_width=True):
        st.session_state.active_tab = "Refactor"
    if st.button("🧪 Generate Tests", use_container_width=True):
        st.session_state.active_tab = "Tests"

    st.divider()

    # ── Status
    status_color = "✅" if st.session_state.project_loaded else "⚪"
    st.markdown(f"{status_color} **Codebase:** {'Loaded' if st.session_state.project_loaded else 'Not loaded'}")
    st.markdown(f"💬 **Turns:** {len(st.session_state.chat_history)}")

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.memory = []
        st.rerun()


# ─── Main layout: Code Editor | AI Panel ──────────────────────────────────────
editor_col, chat_col = st.columns([1, 1], gap="medium")

# ──────────────────────────────────────────────────────────────────────────────
# LEFT: Code Editor Panel
# ──────────────────────────────────────────────────────────────────────────────
with editor_col:
    file_label = st.session_state.selected_file or "No file open"
    st.markdown(
        f'<div class="panel-header">📝 Code Editor — <span style="color:#3b82f6">{file_label}</span></div>',
        unsafe_allow_html=True,
    )

    code_input = st.text_area(
        "code_editor",
        value=st.session_state.selected_file_content,
        height=400,
        label_visibility="collapsed",
        placeholder="# Paste your code here, or open a file from the sidebar...",
        key="code_editor_area",
    )

    lang_col, action_col = st.columns([1, 2])
    with lang_col:
        language = st.selectbox(
            "Language",
            ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "Other"],
            label_visibility="collapsed",
        )
    with action_col:
        explain_level = st.selectbox(
            "Level",
            ["beginner", "intermediate", "expert"],
            index=1,
            label_visibility="collapsed",
        )


# ──────────────────────────────────────────────────────────────────────────────
# RIGHT: AI Panel with tabs
# ──────────────────────────────────────────────────────────────────────────────
with chat_col:
    st.markdown('<div class="panel-header">🤖 AI Assistant</div>', unsafe_allow_html=True)

    tab_chat, tab_debug, tab_generate, tab_refactor, tab_tests = st.tabs([
        "💬 Chat", "🐛 Debug", "✨ Generate", "🔧 Refactor", "🧪 Tests"
    ])

    # ── CHAT TAB ─────────────────────────────────────────────────────────────
    with tab_chat:
        # Chat history display
        chat_container = st.container(height=420)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    '<div style="color:#475569;text-align:center;padding:40px 0;font-size:14px;">'
                    '🤖 Ask anything about your code...<br>'
                    '<span style="font-size:12px">Tip: The AI auto-detects whether you want to debug, explain, generate, or optimize.</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            for turn in st.session_state.chat_history:
                render_chat_message(turn)

        # Input row
        msg_col, send_col = st.columns([4, 1])
        with msg_col:
            user_message = st.text_input(
                "message",
                placeholder="Ask about your code, request a fix, or generate something...",
                label_visibility="collapsed",
                key="chat_input",
            )
        with send_col:
            send_btn = st.button("Send ↗", use_container_width=True, key="send_chat")

        if send_btn and user_message:
            with st.spinner("Thinking..."):
                result = api_post("query", {
                    "message": user_message,
                    "code": code_input,
                    "explain_level": explain_level,
                    "memory": st.session_state.memory,
                })

            if result:
                turn = {
                    "user": user_message,
                    "assistant": result["response"],
                    "intent": result.get("intent", "query"),
                    "code_blocks": result.get("code_blocks", []),
                }
                st.session_state.chat_history.append(turn)
                st.session_state.memory.append({
                    "user": user_message,
                    "assistant": result["response"],
                })
                st.session_state.last_response = result
                st.rerun()

    # ── DEBUG TAB ────────────────────────────────────────────────────────────
    with tab_debug:
        st.markdown("**Paste error message or traceback:**")
        error_msg = st.text_area(
            "error_input",
            height=120,
            placeholder="Traceback (most recent call last):\n  File ...\nAttributeError: ...",
            label_visibility="collapsed",
        )

        if st.button("🐛 Debug It", use_container_width=True, key="debug_btn"):
            if not error_msg:
                st.warning("Please paste an error message")
            elif not code_input:
                st.warning("Please paste or load the buggy code in the editor")
            else:
                with st.spinner("Analyzing bug..."):
                    result = api_post("debug", {
                        "code": code_input,
                        "error_message": error_msg,
                        "language": language,
                    })

                if result:
                    # Diff view
                    st.markdown("#### 🔍 Analysis")
                    st.markdown(result["response"])

                    if result.get("code_blocks"):
                        st.markdown("#### ⚡ Side-by-Side Diff")
                        orig_col, fix_col = st.columns(2)
                        with orig_col:
                            st.markdown(
                                '<div class="panel-header" style="color:#ef4444">❌ Original</div>',
                                unsafe_allow_html=True,
                            )
                            st.code(code_input, language=language.lower())
                        with fix_col:
                            st.markdown(
                                '<div class="panel-header" style="color:#22c55e">✅ Fixed</div>',
                                unsafe_allow_html=True,
                            )
                            st.code(result["code_blocks"][0], language=language.lower())

                        if st.button("✏️ Apply Fix to Editor"):
                            st.session_state.selected_file_content = result["code_blocks"][0]
                            st.rerun()

    # ── GENERATE TAB ─────────────────────────────────────────────────────────
    with tab_generate:
        st.markdown("**Describe what you want to generate:**")
        gen_prompt = st.text_area(
            "gen_prompt",
            height=100,
            placeholder="e.g. A function that takes a list of numbers and returns the top N sorted values",
            label_visibility="collapsed",
        )

        if st.button("✨ Generate Code", use_container_width=True, key="gen_btn"):
            if not gen_prompt:
                st.warning("Enter a description")
            else:
                with st.spinner("Generating..."):
                    result = api_post("generate", {
                        "prompt": gen_prompt,
                        "language": language,
                        "context_code": code_input,
                    })

                if result:
                    st.markdown(result["response"])
                    if result.get("code_blocks"):
                        if st.button("✏️ Load to Editor", key="gen_load"):
                            st.session_state.selected_file_content = result["code_blocks"][0]
                            st.rerun()

    # ── REFACTOR TAB ─────────────────────────────────────────────────────────
    with tab_refactor:
        st.markdown("**Refactoring instructions (optional):**")
        refactor_instructions = st.text_input(
            "refactor_instr",
            value="Improve readability, rename variables, and break large functions.",
            label_visibility="collapsed",
        )

        if st.button("🔧 Refactor Code", use_container_width=True, key="refactor_btn"):
            if not code_input:
                st.warning("Load or paste code in the editor first")
            else:
                with st.spinner("Refactoring..."):
                    result = api_post("refactor", {
                        "code": code_input,
                        "instructions": refactor_instructions,
                        "language": language,
                    })

                if result:
                    st.markdown(result["response"])
                    if result.get("code_blocks"):
                        ref_orig, ref_new = st.columns(2)
                        with ref_orig:
                            st.markdown("**Original**")
                            st.code(code_input, language=language.lower())
                        with ref_new:
                            st.markdown("**Refactored**")
                            st.code(result["code_blocks"][0], language=language.lower())

                        if st.button("✏️ Apply Refactor", key="apply_refactor"):
                            st.session_state.selected_file_content = result["code_blocks"][0]
                            st.rerun()

    # ── TESTS TAB ────────────────────────────────────────────────────────────
    with tab_tests:
        st.markdown("**Test Framework:**")
        framework = st.selectbox(
            "Framework",
            ["pytest", "unittest", "jest", "mocha"],
            label_visibility="collapsed",
        )

        if st.button("🧪 Generate Tests", use_container_width=True, key="tests_btn"):
            if not code_input:
                st.warning("Load or paste code in the editor first")
            else:
                with st.spinner("Generating test suite..."):
                    result = api_post("tests", {
                        "code": code_input,
                        "framework": framework,
                        "language": language,
                    })

                if result:
                    st.markdown("**Generated Test Suite:**")
                    st.markdown(result["response"])

                    if result.get("code_blocks"):
                        if st.button("📋 Copy Tests", key="copy_tests"):
                            st.code(result["code_blocks"][0], language=language.lower())
