import anthropic
import voyageai
import chromadb
import os
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
import json

load_dotenv()
ant_client = anthropic.Anthropic()
vo_client = voyageai.Client()
chroma_client = chromadb.CloudClient(
    api_key= os.getenv('CHROMA_API_KEY'),
    database= os.getenv('CHROMA_DATABASE'),
    tenant= os.getenv('CHROMA_TENANT')
)

def claude(system,prompt):
    response = ant_client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        system = system,
        messages = [{'role': 'user', 'content': prompt}]
    )
    return next((b.text for b in response.content if b.type == 'text'),'No response')

class inputstate(TypedDict):
    question: str
    coll_name: str

class overallstate(TypedDict):
    question: str
    coll_name: str
    sub_questions: list[str]
    rag_results: dict[list[str]]
    synthesis: str
    result: str

class outputstate(TypedDict):
    result: str


def retrieve(state: inputstate)-> dict:
    embeddings = vo_client.embed([state['question']], model = 'voyage-3', input_type = 'query').embeddings
    coll = chroma_client.get_collection(state['coll_name'])
    docs = coll.query(query_embeddings=embeddings, include= ['metadatas', 'documents'], n_results = 3)
    return {'rag_results':{
        'ids': docs['ids'][0],
        'docs': docs['documents'][0]
    }}

def answer(state: overallstate) -> dict:
    system = 'You are a helpful assistant. Answer the question using ONLY the provided sources. Cite sources inline as [source_id].'
    rag = state['rag_results']
    if isinstance(rag, str):
        try:
            rag = json.loads(rag)
        except (json.JSONDecodeError, TypeError):
            print('Invalid format. Expected: {"ids": [...], "docs": [...]}')
            return {'result': 'Aborted — invalid rag_results format provided.'}
    sources = "\n".join([
        f"{rag['ids'][i]}: {rag['docs'][i]}"
        for i in range(len(rag['ids']))
    ])
    prompt = f"Question: {state['question']}\nSources:\n{sources}"
    response = claude(system, prompt)
    return {'result': response}

graph = StateGraph(overallstate,input_schema=inputstate,output_schema=outputstate)

graph.add_node(retrieve)
graph.add_node(answer)

graph.add_edge(START,'retrieve')
graph.add_edge('retrieve','answer')
graph.add_edge('answer',END)

query_app = graph.compile()
