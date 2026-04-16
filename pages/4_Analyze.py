import streamlit as st
import requests
from utils import check_password, get_headers, API_BASE

check_password()
st.set_page_config(page_title = '📰 News Analyzer', layout= 'centered')
st.title('News Analyzer')
st.markdown('**Returns a summary and list of key topics**')
article = st.text_area('Enter your article here', height = 300)
if article:
    try:
        with st.spinner('Analyzing....'):
            resp = requests.post(
                f'{API_BASE}/analyze',
                json={'article': article },
                headers=get_headers()
            )
            resp.raise_for_status()
            data = resp.json()
        
            st.subheader('Summary')
            st.markdown(data['response'].get('summary','Summary unavailable'))
            key_topics = data['response'].get('key_topics')
            st.divider()
            st.subheader('Key topics')
            if key_topics:
                for topic in key_topics:
                    st.markdown(f'- {topic}')
            else:
                st.markdown('None')
            st.caption(f'↑ {data["input_tokens"]} tokens  ↓ {data["output_tokens"]} tokens')
    except requests.HTTPError as e:
        reply = f'Error: {e.response.status_code} — {e.response.text}'
        st.error(reply)
    except Exception as e:
        reply = f'Error: {e}'
        st.error(reply)