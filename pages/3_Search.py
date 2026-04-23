import streamlit as st
from utils import check_password
from ingest import ingest_app
from query import query_app
import uuid
from chromadb.errors import NotFoundError
import tempfile
import os

check_password()
if 'search_session_id' not in st.session_state:
    st.session_state.search_session_id = str(uuid.uuid4())
if 'ingested_files' not in st.session_state:
    st.session_state.ingested_files = []

st.set_page_config(page_title='Search', layout='centered')
st.title('🔍 Search')
st.subheader('Document Q&A')

file = st.file_uploader('Upload a file (pdf, txt or md)', type=['pdf', 'txt', 'md'])


prompt = st.chat_input('Type a query')

with st.sidebar:
    n = st.slider(label='Number of documents', min_value=1, max_value=10, value=3)

if file and file.name in st.session_state.ingested_files:
    st.markdown('File already ingested')
if file and file.name not in st.session_state.ingested_files:
    st.session_state.ingested_files.append(file.name)
    with st.spinner('Ingesting document...'):
        try:
            suffix = os.path.splitext(file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file.read())
                tmp_path = tmp.name
            count = ingest_app.invoke({'file_path': tmp_path, 'coll_name': st.session_state.search_session_id})
            os.unlink(tmp_path)
            st.markdown(f'{count["count"]} chunks saved')
        except ValueError:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
            st.error('Error: Unsupported file type')

if prompt:
    st.markdown(f'**Query:** {prompt}')
    st.markdown('**Results:**')
    with st.spinner('Fetching...'):
        try:
            resp = query_app.invoke({'question': prompt, 'coll_name': st.session_state.search_session_id})
            st.markdown(resp['result'])
        except (ValueError, NotFoundError):
            st.error('Please upload a file first')
        except Exception as e:
            st.error(f'Error: {e}')