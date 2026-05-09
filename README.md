# 🤖 AI Coding Assistant Agent

A local AI-powered developer copilot with RAG (Retrieval-Augmented Generation), multi-modal code intelligence, and a VS Code-inspired dark UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Codebase Ingestion** | Load any project folder, embed with FAISS, query with RAG |
| 🐛 **Debugging Agent** | Paste error → get explanation + root cause + fixed code |
| 💬 **AI Chat** | Auto-detects intent (debug/explain/generate/refactor/test) |
| ✨ **Code Generator** | Generate functions/classes from natural language |
| 🔧 **Refactor Agent** | Rename, simplify, restructure with explanations |
| 🧪 **Test Generator** | Full pytest/unittest/jest suites with edge cases |
| 📊 **Code Explanation** | Beginner / Intermediate / Expert levels |
| 🧠 **Memory System** | Remembers last 3 conversation turns per session |
| 🔄 **Diff View** | Side-by-side original vs fixed/refactored code |

---

## 🧱 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Streamlit Frontend (port 8501)            │
│   Sidebar | Code Editor | AI Panel (Chat/Debug/Gen/Tests)   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP (requests)
┌─────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend (port 8000)                 │
│  /query  /debug  /generate  /refactor  /tests               │
│                                                             │
│  Agent → Intent Detection → RAG Retrieve → LLM → Response  │
└──────────┬───────────────────────────────┬──────────────────┘
           │                               │
    ┌──────▼──────┐               ┌────────▼────────┐
    │ FAISS Index │               │   OpenAI API    │
    │ (local disk)│               │  (GPT-4o)       │
    └─────────────┘               └─────────────────┘
```

---

## 📁 Project Structure

```
ai-coding-assistant/
├── backend/
│   ├── app.py                  # FastAPI entry point
│   ├── routes/
│   │   ├── upload.py           # POST /upload_codebase
│   │   ├── query.py            # POST /query
│   │   ├── debug.py            # POST /debug
│   │   ├── generate.py         # POST /generate
│   │   ├── refactor.py         # POST /refactor
│   │   └── tests.py            # POST /tests
│   ├── services/
│   │   ├── llm_service.py      # OpenAI API abstraction
│   │   ├── code_analyzer.py    # Static code analysis
│   │   └── agent.py            # Intent detection + routing
│   ├── rag/
│   │   ├── ingest.py           # FAISS indexing
│   │   └── retrieve.py         # Semantic retrieval
│   └── utils/
│       ├── file_loader.py      # Project file walker
│       └── chunker.py          # Code chunking for RAG
├── frontend/
│   └── app.py                  # Streamlit 3-panel UI
├── data/
│   └── vector_store/           # FAISS index (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone <repo-url>
cd ai-coding-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
nano .env
```

Required:
```
OPENAI_API_KEY=sk-your-actual-key
```

---

## 🚀 Running the App

### Terminal 1 — Start the Backend

```bash
cd backend
uvicorn app:app --reload --port 8000
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 — Start the Frontend

```bash
cd frontend
streamlit run app.py
```

Open: **http://localhost:8501**

---

## 🧪 Testing Features

### Via UI (Streamlit)

1. **Chat Mode** — Type any question in the Chat tab. The agent auto-detects intent.
   - "What does this function do?" → Explain
   - "Fix this error: NameError..." → Debug
   - "Write a function to sort..." → Generate

2. **Debug Mode** — Paste buggy code in editor + error in Debug tab → Click Debug It

3. **Ingest Codebase** — Enter a local project path in the sidebar → Click Ingest Codebase

4. **Generate** — Go to Generate tab, describe what you want

5. **Refactor** — Paste code in editor → Refactor tab → Click Refactor Code

6. **Tests** — Paste code in editor → Tests tab → Choose framework → Generate Tests

### Via API (curl)

```bash
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain what a decorator is in Python"}'

# Debug
curl -X POST http://localhost:8000/api/debug \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + c",
    "error_message": "NameError: name '\''c'\'' is not defined"
  }'

# Generate
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A function to calculate fibonacci numbers", "language": "Python"}'

# Ingest a local project
curl -X POST http://localhost:8000/api/upload_codebase \
  -H "Content-Type: application/json" \
  -d '{"project_dir": "/path/to/your/project"}'
```

---

## 🔌 API Reference

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| `POST` | `/api/upload_codebase` | `{project_dir}` | ingestion summary |
| `POST` | `/api/query` | `{message, code?, explain_level?, memory?}` | `{intent, response, code_blocks}` |
| `POST` | `/api/debug` | `{code, error_message, language?}` | `{response, code_blocks, error_info}` |
| `POST` | `/api/generate` | `{prompt, language?, context_code?}` | `{response, code_blocks}` |
| `POST` | `/api/refactor` | `{code, instructions?, language?}` | `{response, code_blocks}` |
| `POST` | `/api/tests` | `{code, framework?, language?}` | `{response, code_blocks}` |

---

## 🔮 Extending

### Swap LLM to Ollama

Edit `backend/services/llm_service.py`:
```python
from openai import OpenAI

# Replace:
self.client = OpenAI(api_key=self.api_key)

# With:
self.client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy key
)
self.model = "codellama:13b"
```

### Add a new route

1. Create `backend/routes/myfeature.py`
2. Register in `backend/app.py`: `app.include_router(myfeature.router, prefix="/api")`
3. Add UI in `frontend/app.py`

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | Make sure backend is running: `uvicorn app:app --port 8000` |
| `OpenAI API error` | Check `OPENAI_API_KEY` in `.env` |
| `No files found` | Ensure the project path exists and has supported file types |
| `FAISS not found` | Run `pip install faiss-cpu` |

---

## 📄 License

MIT License — use freely, modify, and extend.
