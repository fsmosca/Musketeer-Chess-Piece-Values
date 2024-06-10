import streamlit as st
from streamlit import session_state as ss
from deta import Deta
from module.nav import Nav
import pandas as pd
import urllib.request
import urllib.error
from module.data import PT_IMAGE


st.set_page_config(layout='wide', page_title=st.secrets['page_title'])


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
    st.switch_page('pages/login.py')

if 'dbc' not in ss:
    ss.dbc = None

if 'admins' not in ss:
    ss.admins = True


if not ss.is_login:
    st.switch_page('pages/login.py')


@st.cache_resource(ttl=3600)
def read_deta_db():
    detap = Deta(st.secrets["deta_key"])
    dbd = detap.Base("piecevalue")
    return dbd


st.logo('assets/images/logo.png', link='https://www.musketeerchess.net/p/home/index.html')
Nav()

if ss.username == st.secrets['admin1']:
    ss.admins = False

st.header('Piece Values')

db = read_deta_db()

tab1, tab2 = st.tabs(['🔥 Piece Value', '📘 Data Input'])

with tab1:
    ss.dbc = db.fetch().items
    df = pd.DataFrame(ss.dbc)
    df = df[['key', 'PieceType', 'Variant', 'Middle', 'Ending', 'Mean']]

    cols = st.columns([1, 1], gap='large')

    with cols[0]:
        st.markdown('### Piece Type List')
        cols2 = st.columns([1, 1, 1, 1])
        cols2[0].checkbox('Chess', value = False, key='chessk')
        cols2[1].checkbox('MC1', value = False, key='mc1k')
        cols2[2].checkbox('MC1.1', value = False, key='mc11k')

        variants = []
        if ss.mc1k:
            variants.append('MC1')
        if ss.chessk:
            variants.append('Chess')
        if ss.mc11k:
            variants.append('MC1.1')

        # Filter the DataFrame based on the variants list
        if variants:
            df_filtered = df[df['Variant'].isin(variants)]
        else:
            df_filtered = df

        df_filtered = df_filtered.reset_index(drop=True)

        event = st.dataframe(df_filtered, hide_index=True, on_select='rerun', height=500, use_container_width=True)

    selected_info = event['selection']

    with cols[1]:
        st.markdown('### Selected Pieces')
        holder = st.empty()
        df_selected = df_filtered.loc[selected_info['rows']]
        df_selected = df_selected.reset_index(drop=True)
        event2 = st.dataframe(df_selected, hide_index=True, on_select='rerun', selection_mode='single-row', use_container_width=True)
        selected_info2 = event2['selection']
        holder.markdown(f"**Total Mean Value: {df_selected['Mean'].sum().round(0)}**")
        if len(selected_info2['rows']):
            ri = selected_info2['rows'][0]
            pt = df_selected.loc[ri, 'PieceType']
            url = PT_IMAGE.get(pt)
            st.markdown(f'**{pt}**')
            if url:
                st.image(url, width=250)
            

with tab2:
    cols = st.columns([1, 1], gap='small')

    with cols[0]:
        with st.form("form", clear_on_submit=False):
            pt = st.text_input("piece type")
            k = st.text_input("key")
            var = st.text_input("variant")
            op = st.number_input("middle value", value=100, min_value=0, max_value=5000, step=1)
            en = st.number_input("ending value", value=100, min_value=0, max_value=5000, step=1)
            submitted = st.form_submit_button("Store in database", disabled=ss.admins)

        if submitted:
            mean_value = int((op + en) / 2)
            try:
                db.insert({"PieceType": pt, "Middle": op, "Ending": en, "Mean": mean_value, "Variant": var, "key": k})
            except urllib.error.HTTPError as e:
                if e.code == 409:
                    st.error(f"HTTP Error 409: Conflict - A key has already existed")
                else:
                    st.error(f"HTTP Error {e.code}: {e.reason}")

            except urllib.error.URLError as e:
                st.error(f"URL Error: {e.reason}")

            except Exception as e:
                st.error(f"Unexpected error: {e}")
            else:
                st.success('Data is successfully saved!!')
