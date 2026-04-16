import streamlit as st
import requests
import uuid
from utils import check_password, get_headers, API_BASE

check_password()

st.set_page_config(page_title='Chat', layout='centered')
st.title('💬 Chat')

if 'chat_session_id' not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

if st.button('Clear history'):
    requests.delete(
        f'{API_BASE}/chat/{st.session_state.chat_session_id}',
        headers=get_headers()
    )
    st.session_state.chat_messages = []
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.rerun()

prompt = st.chat_input('Type a message')
if prompt:
    st.session_state.chat_messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Thinking...'):
            try:
                resp = requests.post(
                    f'{API_BASE}/chat',
                    json={'message': prompt, 'session_id': st.session_state.chat_session_id},
                    headers=get_headers()
                )
                resp.raise_for_status()
                data = resp.json()
                reply = data['response']
                st.markdown(reply)
                st.caption(f'↑ {data["input_tokens"]} tokens  ↓ {data["output_tokens"]} tokens')
            except requests.HTTPError as e:
                reply = f'Error: {e.response.status_code} — {e.response.text}'
                st.error(reply)
            except Exception as e:
                reply = f'Error: {e}'
                st.error(reply)

    st.session_state.chat_messages.append({'role': 'assistant', 'content': reply})