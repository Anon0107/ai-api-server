from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import anthropic
import voyageai
import chromadb
from dotenv import load_dotenv
import os
import textwrap
import json
import time
import asyncio
from collections import defaultdict

load_dotenv()
app = FastAPI()
vo_client = voyageai.Client()
chroma_client = chromadb.CloudClient(
    api_key = os.getenv('CHROMA_API_KEY'),
    database = os.getenv('DATABASE'),
    tenant = os.getenv('CHROMA_TENANT')
)
ant_client = anthropic.AsyncAnthropic()
request_log = defaultdict(list)
API_KEY = os.getenv('API_KEY')

def check_rate_limit(client_ip: str):
    current = time.time()
    back = current - 60
    request_log[client_ip] = [t for t in request_log[client_ip] if t > back]
    if len(request_log[client_ip]) >= 10:
        raise(HTTPException(status_code = 429, detail = 'Rate limit exceeded'))
    request_log[client_ip].append(current)

def check_auth(api_key: str = Header(None)):
    if api_key != API_KEY:
        raise(HTTPException(status_code = 401, detail= 'Invalid or missing APi key'))

class ChatRequest(BaseModel):
    message: str = Field(...,min_length = 1,max_length = 10000)

@app.post('/chat')
async def post_chat(body: ChatRequest, request: Request, api_key: str = Header(None)):
    check_auth(api_key)
    check_rate_limit(request.client.host)
    response = await ant_client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system='You are a helpful assistant that responds gracefully.',
        messages=[{'role': 'user', 'content': body.message}]
    )
    reply = next((b.text for b in response.content if b.type == 'text'), 'No response')
    return {
        'message': body.message,
        'response': reply,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens
    }

class AnalyzeRequest(BaseModel):
    article: str = Field(...,min_length = 10, max_length =10000)

@app.post('/analyze')
async def post_analyze(body: AnalyzeRequest, request: Request, api_key: str = Header(None)):
    check_auth(api_key)
    check_rate_limit(request.client.host)
    response = await ant_client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system='You are an article analyzer. Respond only with a valid JSON object. No explanation. No prose.',
        messages=[
            {'role': 'user', 'content': textwrap.dedent(f'''
                <article>{body.article}</article>
                <structure>
                {{
                    "summary": "one line summary",
                    "key_topics": ["topic_1", "topic_2"]
                }}
                </structure>
            ''').strip()},
            {'role': 'assistant', 'content': '{'}
        ]
    )
    reply = next((b.text for b in response.content if b.type == 'text'), None)
    if reply is None:
        return {'error': 'No response from model'}
    parsed = json.loads('{' + reply)
    return {
        'article': body.article,
        'response': parsed,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens
    }

class SearchRequest(BaseModel):
    query: str = Field(...,min_length= 1, max_length= 100)
    n_results: int = Field(3,ge = 1, le = 10)

@app.post('/search')
def post_search(body: SearchRequest, request: Request, api_key: str = Header(None)):
    check_auth(api_key)
    check_rate_limit(request.client.host)
    embeddings = vo_client.embed([body.query], model = 'voyage-3', input_type = 'query').embeddings
    coll = chroma_client.get_collection('notes')
    result = coll.query(
        query_embeddings = embeddings,
        n_results = body.n_results
    )
    return {
        'query': body.query,
        'n_results': body.n_results,
        'documents': result['documents'][0]
    }
import uuid

conversation_history: dict[str, list] = defaultdict(list)

class StreamRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), min_length=1, max_length=100)

async def stream_claude(body: StreamRequest):
    history = conversation_history[body.session_id]
    history.append({'role': 'user', 'content': body.message})

    est_tokens = await ant_client.messages.count_tokens(
        model='claude-haiku-4-5-20251001',
        system='You are a helpful assistant.',
        messages=history
    )
    if est_tokens.input_tokens > 4000:
        last_message = history.pop()
        history.append({'role': 'user', 'content': 'Summarize this conversation into a single concise message. Only respond with the message'})
        summary_resp = await ant_client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=512,
            system='You are a helpful assistant.',
            messages=history
        )
        summary = next((b.text for b in summary_resp.content if b.type == 'text'), '')
        conversation_history[body.session_id] = [
            {'role': 'user', 'content': f'Context summary: {summary}. {last_message["content"]}'}
        ]
        history = conversation_history[body.session_id]

    async with ant_client.messages.stream(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system='You are a helpful assistant.',
        messages=history
    ) as stream:
        async for text in stream.text_stream:
            yield f'data: {text}\n\n'
        full_reply = stream.get_full_text()
    history.append({'role': 'assistant', 'content': full_reply})
    yield 'data: [DONE]\n\n'

@app.post('/stream')
async def post_stream(body: StreamRequest, request: Request, api_key: str = Header(None)):
    check_auth(api_key)
    check_rate_limit(request.client.host)
    return StreamingResponse(
        stream_claude(body),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        },
    )

@app.delete('/stream/{session_id}')
async def clear_stream(session_id: str, request: Request, api_key: str = Header(None)):
    check_auth(api_key)
    conversation_history.pop(session_id, None)
    return {'session_id': session_id, 'cleared': True}
