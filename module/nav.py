import streamlit as st



def Home():
    st.sidebar.page_link('streamlit_app.py', label='Home', icon='🏡')


def Login():
    st.sidebar.page_link('pages/login.py', label='Login', icon='🔑')


def PieceValue():
    st.sidebar.page_link('pages/piece_value.py', label='Piece Values', icon='🔥')


def Nav():
    Home()
    Login()
    PieceValue()

