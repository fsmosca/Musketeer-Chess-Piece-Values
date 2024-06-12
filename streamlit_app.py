import streamlit as st
from streamlit import session_state as ss
from module.nav import Nav


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


if 'is_login' not in ss:
    ss.is_login = False
    st.switch_page('pages/login.py')

if not ss.is_login:
    st.switch_page('pages/login.py')


st.logo('assets/images/logo.png', link='https://www.musketeerchess.net/p/home/index.html')
Nav()

st.header(f'{st.secrets["main_title"]}')

st.markdown('''
:blue[**Musketeer Chess**] is a modern variant of traditional chess introduced by :green[**Zied Haddad**]. It incorporates new pieces and mechanics to add variety and complexity to the game.
            
The primary objective remains the same as in traditional chess - **to checkmate the opponent's king**. However, the new pieces and setup phase add layers of strategy and unpredictability.

Musketeer Chess aims to **rejuvenate interest in chess** by offering a fresh take on the classic game, appealing to both traditional players and those looking for new challenges.
''')
