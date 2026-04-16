# AI API Server

A FastAPI backend exposing AI-powered endpoints built with Claude Haiku, Voyage AI embeddings, and ChromaDB. Includes a Streamlit frontend deployed at [ai-api-server-a5ml2ddh2awwtdqsy2qs6e.streamlit.app](https://ai-api-server-a5ml2ddh2awwtdqsy2qs6e.streamlit.app).

## Stack

- FastAPI + Uvicorn
- Anthropic Claude Haiku (`claude-haiku-4-5-20251001`)
- Voyage AI (embeddings)
- ChromaDB Cloud (vector store)
- Streamlit (frontend)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Non-streaming chat with per-session conversation history |
| DELETE | `/chat/{session_id}` | Clear chat history for a specific session |
| POST | `/analyze` | Analyze an article, returns structured JSON (summary, key topics) |
| POST | `/search` | Semantic search over ChromaDB using Voyage AI embeddings |
| POST | `/stream` | Streaming chat via Server-Sent Events with per-session conversation history |
| DELETE | `/stream/{session_id}` | Clear stream history for a specific session |

## Frontend Pages

| Page | Description |
|------|-------------|
| Chat | Conversational assistant with session history |
| Stream | Same assistant with token-by-token streaming via SSE |
| Document Q&A | Semantic search over a BanG Dream database |
| News Analyzer | Extracts summary and key topics from any article |

## Setup

```bash
py -3.11 -m pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
py -3.11 -m uvicorn main:app --reload
```

## Deployment

- **Backend:** Render (https://ai-api-server-528q.onrender.com)
- **Frontend:** Streamlit Community Cloud (https://ai-api-server-a5ml2ddh2awwtdqsy2qs6e.streamlit.app)

## Security

All endpoints require an `api-key` header:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'api-key: YOUR_KEY' \
  -d '{"message": "hello", "session_id": "optional-session-id"}'
```

**Rate limiting:** 10 requests/minute per IP. Exceeding returns `429`.

**Input validation:** All fields have min/max constraints enforced by Pydantic. Invalid input returns `422`.

**Break test results:**

| Test | Status |
|------|--------|
| No API key | 401 |
| Wrong API key | 401 |
| Empty message | 422 |
| Message > 10000 chars | 422 |
| Valid request | 200 |
| 11th request in 60s | 429 |

## Notes

- `/search` uses Voyage AI's sync client — blocking under high load. Acceptable for current scale.
- All other endpoints are fully async.
- Session history is stored in-memory — resets on server restart.
- Streamlit frontend manages session IDs via `st.session_state`, one UUID per browser tab.