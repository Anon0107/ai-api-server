from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
import voyageai
import chromadb
from dotenv import load_dotenv
import os
import textwrap
import json

load_dotenv()
app = FastAPI()
ant_client = anthropic.Anthropic()
vo_client = voyageai.Client()
chroma_client = chromadb.CloudClient(
    api_key = os.getenv('CHROMA_API_KEY'),
    database = os.getenv('DATABASE'),
    tenant = os.getenv('CHROMA_TENANT')
)

class ChatRequest(BaseModel):
    message: str

@app.post('/chat')
def post_chat(request: ChatRequest):
    response = ant_client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system='You are a helpful assistant that responds gracefully.',
        messages=[{'role': 'user', 'content': request.message}]
    )
    reply = next((b.text for b in response.content if b.type == 'text'), 'No response')
    return {
        'message': request.message,
        'response': reply,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens
    }

class AnalyzeRequest(BaseModel):
    article: str

@app.post('/analyze')
def post_analyze(request: AnalyzeRequest):
    response = ant_client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        system='You are an article analyzer. Respond only with a valid JSON object. No explanation. No prose.',
        messages=[
            {'role': 'user', 'content': textwrap.dedent(f'''
                <article>{request.article}</article>
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
        'article': request.article,
        'response': parsed,
        'input_tokens': response.usage.input_tokens,
        'output_tokens': response.usage.output_tokens
    }

class SearchRequest(BaseModel):
    query: str
    n_results: int = 3

@app.post('/search')
def post_search(request: SearchRequest):
    embeddings = vo_client.embed([request.query], model = 'voyage-3', input_type = 'query').embeddings
    coll = chroma_client.get_collection('notes')
    result = coll.query(
        query_embeddings = embeddings,
        n_results = request.n_results
    )
    return {
        'query': request.query,
        'n_results': request.n_results,
        'documents': result['documents'][0]
    }