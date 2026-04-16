import streamlit as st
import requests
from utils import check_password, get_headers, API_BASE

check_password()

st.set_page_config(page_title='Search', layout='centered')
st.title('🔍 Search')
st.subheader('From a BanG Dream Database')

prompt = st.chat_input('Type a query')
with st.sidebar:
    n = st.slider(label='Number of documents', min_value=1, max_value=10, value=3)
if prompt:
    st.markdown(f'**Query:** {prompt}')
    st.markdown('**Results:** ')

    with st.spinner('Fetching...'):
        try:
            resp = requests.post(
                f'{API_BASE}/search',
                json={'query': prompt,'n_results': n },
                headers=get_headers()
            )
            resp.raise_for_status()
            data = resp.json()
            docs = data['documents']
            for index,doc in enumerate(docs,1):
                st.markdown(f'**Document {index}**')
                st.markdown(doc)
                st.divider()
        except requests.HTTPError as e:
            reply = f'Error: {e.response.status_code} — {e.response.text}'
            st.error(reply)
        except Exception as e:
            reply = f'Error: {e}'
            st.error(reply)
