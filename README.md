# AI API Server

A FastAPI backend exposing AI-powered endpoints built with Claude Haiku, Voyage AI embeddings, and ChromaDB.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send a message, get a Claude response |
| POST | `/analyze` | Analyze an article, returns structured JSON (summary, key topics) |
| POST | `/search` | Semantic search over ChromaDB using Voyage AI embeddings |
| POST | `/stream` | Streaming chat via Server-Sent Events — tokens arrive in real time |

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

## Notes

- `/search` uses Voyage AI's sync client — blocking under high load. Acceptable for current scale.
- All other endpoints are fully async.