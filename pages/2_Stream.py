import streamlit as st
import requests
import uuid
from utils import check_password, get_headers, API_BASE

check_password()

st.set_page_config(page_title='Stream', layout='centered')
st.title('🌊 Stream')

if 'stream_session_id' not in st.session_state:
    st.session_state.stream_session_id = str(uuid.uuid4())
if 'stream_messages' not in st.session_state:
    st.session_state.stream_messages = []

for msg in st.session_state.stream_messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if st.button('Clear history'):
    requests.delete(
        f'{API_BASE}/stream/{st.session_state.stream_session_id}',
        headers=get_headers()
    )
    st.session_state.stream_messages = []
    st.session_state.stream_session_id = str(uuid.uuid4())
    st.rerun()

def stream_response(prompt: str, session_id: str):
    with requests.post(
        f'{API_BASE}/stream',
        json={'message': prompt, 'session_id': session_id},
        headers=get_headers(),
        stream=True
    ) as resp:
        for line in resp.iter_lines():
            if line:
                text = line.decode('utf-8')
                if text.startswith('data: '):
                    chunk = text[6:]
                    if chunk == '[DONE]':
                        return
                    yield chunk

prompt = st.chat_input('Type a message')
if prompt:
    st.session_state.stream_messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        reply = st.write_stream(stream_response(prompt, st.session_state.stream_session_id))

    st.session_state.stream_messages.append({'role': 'assistant', 'content': reply})