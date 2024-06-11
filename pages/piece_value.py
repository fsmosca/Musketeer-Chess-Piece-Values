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


if 'data' not in ss:
    ss.data = {}

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


@st.cache_data
def get_weight_classes():
    df = pd.read_csv('assets/csv/weight_classes.csv')
    return df


def update_detadb(db):
    is_good = True
    if not ss.ukeyk:
        ss.data = {}
        is_good = False
    elif ss.ucatk and ss.uptk:
        ss.data = {'Category': ss.ucatk, 'PieceType': ss.uptk}
    elif ss.ucatk:
        ss.data = {'Category': ss.ucatk}
    elif ss.uptk:
        ss.data = {'PieceType': ss.uptk}
    else:
        ss.data = {}
        is_good = False

    if is_good:
        db.update(ss.data, key=ss.ukeyk)


def scale_value(x):
    """
    Scale a value from one range to another.
    
    Parameters:
        x (float): The original value to scale.
        xmin (float): The minimum value of the original range.
        xmax (float): The maximum value of the original range.
        ymin (float): The minimum value of the new range.
        ymax (float): The maximum value of the new range.
        
    Returns:
        float: The scaled value.
    """
    xmin = 171
    xmax = 3589
    ymin = 105
    ymax = 250

    return ((x - xmin) / (xmax - xmin)) * (ymax - ymin) + ymin


weight_classes = [
    {"name": "Mini Flyweight", "min_lbs": 0, "max_lbs": 105},
    {"name": "Light Flyweight", "min_lbs": 106, "max_lbs": 108},
    {"name": "Flyweight", "min_lbs": 109, "max_lbs": 112},
    {"name": "Super Flyweight", "min_lbs": 113, "max_lbs": 115},
    {"name": "Bantamweight", "min_lbs": 116, "max_lbs": 118},
    {"name": "Super Bantamweight", "min_lbs": 119, "max_lbs": 122},
    {"name": "Featherweight", "min_lbs": 123, "max_lbs": 126},
    {"name": "Super Featherweight", "min_lbs": 127, "max_lbs": 130},
    {"name": "Lightweight", "min_lbs": 131, "max_lbs": 135},
    {"name": "Super Lightweight", "min_lbs": 136, "max_lbs": 140},
    {"name": "Welterweight", "min_lbs": 141, "max_lbs": 147},
    {"name": "Super Welterweight", "min_lbs": 148, "max_lbs": 154},
    {"name": "Middleweight", "min_lbs": 155, "max_lbs": 160},
    {"name": "Super Middleweight", "min_lbs": 161, "max_lbs": 168},
    {"name": "Light Heavyweight", "min_lbs": 169, "max_lbs": 175},
    {"name": "Cruiserweight", "min_lbs": 176, "max_lbs": 200},
    {"name": "Super Cruiserweight", "min_lbs": 201, "max_lbs": 224},
    {"name": "Heavyweight", "min_lbs": 225, "max_lbs": 300}
]


def find_weight_class(weight):
    for weight_class in weight_classes:
        if weight >= weight_classes[17]['min_lbs']:
            return 'Heavyweight'
        
        if weight >= weight_class["min_lbs"] and weight <= weight_class["max_lbs"]:
            return weight_class["name"]
        
    return "Unknown"


st.logo('assets/images/logo.png', link='https://www.musketeerchess.net/p/home/index.html')
Nav()


if ss.username == st.secrets['admin1']:
    ss.admins = False

st.header('Piece Values')

db = read_deta_db()

tab1, tab2, weight_tab = st.tabs(['🔥 Piece Value', '📘 Data Input', '👊 Weight Classes'])

with tab1:
    ss.dbc = db.fetch().items
    df = pd.DataFrame(ss.dbc)
    df = df[['key', 'PieceType', 'Variant', 'Category', 'Middle', 'Ending', 'Mean']]

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

        event = st.dataframe(df_filtered, hide_index=True, on_select='rerun', height=600, use_container_width=True)

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
        st.markdown('### Piece Type Definitions')
        with st.form("form", clear_on_submit=False):
            pt = st.text_input("piece type")
            k = st.text_input("key")
            var = st.selectbox("variant", options=['', 'Chess', 'MC1', 'MC1.1', 'MC2'])
            op = st.number_input("middle value", value=100, min_value=0, max_value=5000, step=1)
            en = st.number_input("ending value", value=100, min_value=0, max_value=5000, step=1)
            submitted = st.form_submit_button("Store in database", disabled=ss.admins)

        if submitted:
            mean_value = int((op + en) / 2)
            scaled_value = scale_value(mean_value)
            weight_class = find_weight_class(scaled_value)
            try:
                db.insert({"PieceType": pt, "Middle": op, "Ending": en, "Mean": mean_value, "Variant": var, "key": k, 'Category': weight_class})
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

    with cols[1]:
        st.markdown('### Update Piece Type Data')
        st.text_input('key', key='ukeyk')
        st.text_input('Update piece type', key='uptk')
        st.selectbox('Update category', options=[''] + list(get_weight_classes()['name']), key='ucatk')
        st.button('Update', type='primary', on_click=update_detadb, args=(db,), disabled=ss.admins)

        st.divider()

        st.markdown('### Piece value to Weight class')

        piece_value = st.text_input('Input Piece Value')
        if piece_value:
            piece_value = int(piece_value)
            scaled_value = scale_value(piece_value)
            scaled_value = int(scaled_value)
            weight_class = find_weight_class(scaled_value)
            st.write(f'Weight lbs: {scaled_value}, WEIGHT CLASS: {weight_class}')

with weight_tab:
    df = pd.read_csv('assets/csv/weight_classes.csv')

    st.markdown('### Weight Classes')
    st.dataframe(df, hide_index=True, height=700)
