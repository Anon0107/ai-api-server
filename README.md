# AI API Server

A FastAPI backend exposing three AI-powered endpoints.

## Endpoints
- `POST /chat` — send a message, get a Claude response
- `POST /analyze` — analyze an article, returns structured JSON (summary, key topics)
- `POST /search` — semantic search over a ChromaDB vector store using Voyage AI embeddings

## Stack
- FastAPI, Anthropic Claude Haiku, Voyage AI, ChromaDB

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
fastapi dev day1.py
```