import streamlit as st

API_BASE = 'https://ai-api-server-528q.onrender.com'

def get_headers():
    return {'api-key': st.secrets['API_KEY']}

def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.set_page_config(page_title='Login', layout='centered')
        st.title('Login')
        password = st.text_input('Password', type='password')
        if st.button('Enter'):
            if password == st.secrets['APP_PASSWORD']:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error('Wrong password')
        st.stop()