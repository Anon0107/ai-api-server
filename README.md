# AI API Server

A FastAPI backend exposing AI-powered endpoints built with Claude Haiku, Voyage AI embeddings, and ChromaDB.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Non-streaming chat with per-session conversation history |
| DELETE | `/chat/{session_id}` | Clear chat history for a specific session |
| POST | `/analyze` | Analyze an article, returns structured JSON (summary, key topics) |
| POST | `/search` | Semantic search over ChromaDB using Voyage AI embeddings |
| POST | `/stream` | Streaming chat via Server-Sent Events with per-session conversation history |
| DELETE | `/stream/{session_id}` | Clear stream history for a specific session |

## Stack

- FastAPI + Uvicorn
- Anthropic Claude Haiku (`claude-haiku-4-5-20251001`)
- Voyage AI (embeddings)
- ChromaDB Cloud (vector store)

## Setup

```bash
py -3.11 -m pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
py -3.11 -m uvicorn server:app --reload
```

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