# AutoStream AI Agent
### Social-to-Lead Agentic Workflow — Built for ServiceHive / Inflx

> A production-ready Conversational AI Agent that converts social media conversations into qualified business leads using **LangGraph**, **Claude 3 Haiku**, **RAG (FAISS)**, and **FastAPI + React**.

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py                  # FastAPI app — /chat, /health, /leads
│   ├── agent/
│   │   ├── state.py             # AgentState TypedDict
│   │   ├── graph.py             # LangGraph StateGraph (nodes + edges)
│   │   ├── nodes.py             # All 5 node functions
│   │   └── tools.py             # mock_lead_capture() + lead log
│   ├── rag/
│   │   ├── loader.py            # JSON → text chunks
│   │   └── vectorstore.py       # FAISS + HuggingFace embeddings
│   └── data/
│       └── knowledge.json       # AutoStream pricing, features, policies
├── frontend/
│   ├── public/index.html
│   └── src/
│       ├── index.js
│       ├── App.js
│       ├── Chat.js              # Full chat UI with intent badge + lead panel
│       └── api.js               # fetch() wrappers for backend
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Local Setup & Run

### Prerequisites
- Python 3.9+
- Node.js 18+
- An **Anthropic API key** (get one at console.anthropic.com)

---

### 1. Clone & enter the project

```bash
git clone <your-repo-url>
cd project
```

### 2. Backend setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt

# Set your environment variable
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`.
- `POST /chat` — main conversation endpoint
- `GET  /health` — health check
- `GET  /leads`  — view all captured leads

### 4. Frontend setup & run

```bash
cd frontend
npm install
npm start
```

The React UI opens at `http://localhost:3000`.

---

## 🏗️ Architecture (~200 words)

The system is built around a **LangGraph StateGraph** — a directed acyclic graph where each node is a pure function that reads from and writes to a shared `AgentState` TypedDict. This replaces linear chain logic with explicit, inspectable routing.

**Graph flow:**

```
classify_intent
    ├─[inquiry/greeting]─► retrieve_docs ─► generate_response
    └─[high_intent]──────► qualify_lead
                               ├─[ready]──► execute_tool ─► generate_response
                               └─[missing fields]──► generate_response
```

**Why LangGraph over plain LangChain?** LangGraph gives us persistent, typed state across turns, conditional branching, and a clear separation between routing logic and node logic — essential for multi-turn lead collection where we must ask for one field at a time and only fire the tool when all three are present.

**State management:** A Python dict keyed by `session_id` holds the full `AgentState` between HTTP calls. Each request appends the new user message, invokes the compiled graph, and merges the result back. The state carries `messages` (full history), `intent`, `retrieved_docs`, `lead_info`, and `is_ready_for_tool`.

**RAG pipeline:** The knowledge base (`knowledge.json`) is split into semantic chunks, embedded with `all-MiniLM-L6-v2` (sentence-transformers), and indexed in a local FAISS vector store. Top-3 relevant chunks are injected into the system prompt at inference time.

---

## 🌐 WhatsApp Integration via Webhooks

To deploy this agent on WhatsApp, use the **Meta Cloud API** (or Twilio for WhatsApp):

### Architecture

```
WhatsApp User
     │
     ▼
Meta / Twilio Webhook  ──POST──►  FastAPI /webhook  endpoint
                                        │
                                        ▼
                                 LangGraph Agent
                                        │
                                        ▼
                              Response text sent back
                              via Meta / Twilio REST API
```

### Implementation Steps

**1. Add a `/webhook` endpoint in `main.py`:**

```python
@app.post("/webhook")
async def whatsapp_webhook(payload: dict):
    # Meta sends messages in this structure:
    entry = payload["entry"][0]["changes"][0]["value"]
    message = entry["messages"][0]
    from_number = message["from"]
    user_text   = message["text"]["body"]

    # Reuse existing chat logic with phone number as session_id
    result = await chat(ChatRequest(message=user_text, session_id=from_number))

    # Send reply via Meta Graph API
    send_whatsapp_reply(from_number, result.response)
    return {"status": "ok"}
```

**2. Verify the webhook** — Meta requires a `GET /webhook` that confirms a `hub.verify_token`.

**3. Send replies** using the Meta Graph API:

```python
import httpx

def send_whatsapp_reply(to: str, text: str):
    httpx.post(
        f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages",
        headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
        json={
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
    )
```

**4. Expose locally** using `ngrok http 8000` and register the HTTPS URL in the Meta developer portal.

**Twilio alternative:** Replace the Meta API calls with `twilio.rest.Client().messages.create(...)` — the webhook shape is identical.

---

## 🎬 Demo Flow

| Turn | User says | Agent behaviour |
|------|-----------|-----------------|
| 1 | "Hi, tell me about your pricing" | RAG retrieval → explains Basic ($29) and Pro ($79) plans |
| 2 | "That sounds great, I want to try the Pro plan for my YouTube channel" | Intent → `high_intent`; asks for name |
| 3 | "My name is Jane Smith" | Extracts name; asks for email |
| 4 | "jane@creator.io" | Extracts email; asks for platform |
| 5 | *(platform already detected as YouTube)* | All fields ready → calls `mock_lead_capture()` → confirmation |

---

## ✅ Evaluation Checklist

| Criterion | Implementation |
|-----------|---------------|
| Agent reasoning & intent detection | LLM-based 3-class classifier in `classify_intent` node |
| Correct RAG use | FAISS + sentence-transformers; top-3 chunks injected into prompt |
| Clean state management | `AgentState` TypedDict; LangGraph merge semantics; session dict |
| Proper tool calling | `execute_tool` fires only when `name + email + platform` all present |
| Code clarity | Modular `nodes.py / graph.py / tools.py / rag/`; fully commented |
| Real-world deployability | FastAPI + CORS; WhatsApp webhook section above; `.env` config |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Your Anthropic API key |

---

*Built for ServiceHive · Inflx assignment — AutoStream Social-to-Lead Agent*
