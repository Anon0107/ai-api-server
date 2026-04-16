import streamlit as st
from utils import check_password

check_password()

st.set_page_config(page_title='AI Assistant', layout='centered')
st.title('AI Assistant')
st.markdown('''
**Pages:**
- 💬 Chat — conversational assistant with history
- 🌊 Stream — same assistant with streaming responses
- 🔍 BanG Dream Document Q&A — semantic search over BanG Dream wiki data
- 📰 News Analyzer — extract summary and topics from any article
''')