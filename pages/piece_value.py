import streamlit as st
from streamlit import session_state as ss
from deta import Deta
from module.nav import Nav
import pandas as pd
import urllib.request
import urllib.error


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


pt_image = {
    'Cannon': 'https://camo.githubusercontent.com/cd95c3c50722f0d876a335665daab55c2efa82195fa3eb673ba5fab76c0a29df/68747470733a2f2f692e696d6775722e636f6d2f4d3176394c5a6a2e706e67',
    'Leopard': 'https://camo.githubusercontent.com/808307273e0738f065680ba457bffa98ff7ac333df40035f9127b62902c5a59b/68747470733a2f2f692e696d6775722e636f6d2f346d36414f7a632e706e67',
    'Unicorn': 'https://camo.githubusercontent.com/cc4a9207d935eb4692228d92ecf46a52672be7269c51df32d9f5329ffd87cdfe/68747470733a2f2f692e696d6775722e636f6d2f617853635632752e706e67',
    'Dragon': 'https://camo.githubusercontent.com/b6dad9d3400b6b725055176328d6e4650e0dcebc4bc352038b5ec435ae2f61bb/68747470733a2f2f692e696d6775722e636f6d2f4b4262307536552e706e67',
    'Chancellor': 'https://camo.githubusercontent.com/bcaafe790474dd99b7a857d2b4efb832529573d5d045bde980954420f6d77e8d/68747470733a2f2f692e696d6775722e636f6d2f346a5a4c7a48422e706e67',
    'Archbishop': 'https://camo.githubusercontent.com/fe5c5ce719f871c981f5c5325ffdf85cc8f078dfc8a245cc06eceb9bedaf7f61/68747470733a2f2f692e696d6775722e636f6d2f6f476531676b632e706e67',
    'Elephant': 'https://camo.githubusercontent.com/4ea2eef6e9c9d0b8a982eb97e2ed263a4a93bcfe300a6df28e4591a9767ea021/68747470733a2f2f692e696d6775722e636f6d2f6a327767464c652e706e67',
    'Hawk': 'https://camo.githubusercontent.com/de904be16c8c43007d1e8bd32d3e4ca3567a623232e3553971f0273092009e22/68747470733a2f2f692e696d6775722e636f6d2f45576d6c616c772e706e67',
    'Fortress': 'https://camo.githubusercontent.com/91070e29832e6f236dfa72241a3186cf10f5201aa22d20243031f59fe7b61302/68747470733a2f2f692e696d6775722e636f6d2f5930726e686b342e706e67',
    'Spider': 'https://camo.githubusercontent.com/98fc95a54ebb8a11aab6a367af39868a1268f7089eb76e10b3e79928397090ab/68747470733a2f2f692e696d6775722e636f6d2f75434438704f412e706e67',
    'IMG450': 'https://user-images.githubusercontent.com/22366935/129747665-8be62ce6-ff9a-4569-889a-6cc79272ef78.png',
    'IMG451': 'https://user-images.githubusercontent.com/22366935/129753259-d4b00d74-1287-4233-975e-29c19f822c1a.png',
    'IMG452': 'https://user-images.githubusercontent.com/22366935/129787330-069921da-a3bf-4815-9cf1-0f30a6025234.png',
}


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
            url = pt_image.get(pt)
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
