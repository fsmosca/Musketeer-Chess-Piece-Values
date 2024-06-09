import streamlit as st
from streamlit import session_state as ss
from deta import Deta
from argon2 import PasswordHasher
from module.nav import Nav
from streamlit_extras.stylable_container import stylable_container


st.set_page_config(layout='centered', page_title=st.secrets['page_title'])


st.markdown("""
    <style>    
           /* Remove blank space at top and bottom */ 
           .block-container {
               padding-top: 1.5rem;
               padding-bottom: 1rem;
            }
    </style>
    """, unsafe_allow_html=True)


ph = PasswordHasher()


if 'is_login' not in ss:
    ss.is_login = False
if 'username' not in ss:
    ss.username = None


deta = Deta(st.secrets["deta_key"])
db = deta.Base("users")


def logout_cb():
    ss.is_login = False
    ss.username = None


st.logo('assets/images/logo.png', link='https://www.musketeerchess.net/p/home/index.html')
Nav()

st.header('Login')

if not ss.is_login:
    with st.form('form'):
        username = st.text_input('username')
        password = st.text_input('password', type='password')
        submitted = st.form_submit_button('Login')

    if submitted:
        if username and password:
            res = db.get(username)
            db_pw_hash = res['password']            
            if ph.verify(db_pw_hash, password):
                ss.is_login = True
                ss.username = username
                st.switch_page('streamlit_app.py')
else:
    st.write(f'Welcome {ss.username}')

    with stylable_container(
        key="Logout",
        css_styles="""
            button {
                background-color: red;
                color: white;
                border-radius: 5px;
            }
            """,):
        st.button("Logout", on_click=logout_cb)
