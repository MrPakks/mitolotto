import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="wide")

# --- ULTRA COMPACT CSS ---
st.markdown("""
    <style>
    /* Usunięcie marginesów bocznych aplikacji */
    .block-container {
        padding: 0.5rem !important;
    }
    
    /* Wymuszenie mikro-siatki */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 1px !important; /* Minimalny odstęp */
        justify-content: center !important;
    }

    [data-testid="column"] {
        flex: 0 0 13% !important; /* Sztywne 13% szerokości */
        min-width: 0px !important;
        padding: 0px !important;
    }

    /* Przyciski: małe kwadraciki 30x30 */
    .stButton > button {
        width: 32px !important; 
        height: 32px !important;
        min-width: 32px !important;
        padding: 0px !important;
        font-size: 11px !important;
        font-weight: bold !important;
        border-radius: 2px !important;
        border: 1px solid #ccc !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    /* Zaznaczony przycisk - wyraźny kolor */
    .stButton > button:active, .stButton > button:focus {
        border-color: #FF4B4B !important;
    }

    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 5px;
    }
    
    /* Ukrycie labeli i zbędnego miejsca */
    iframe { height: 0px; }
    </style>
    """, unsafe_allow_html=True)

DATABASE_FILE = "wyniki.csv"

@st.cache_data
def load_data(source):
    try:
        df = pd.read_csv(source, sep=None, engine='python', header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data']).sort_values('Data')
        df['Rok'] = df['Data'].dt.year
        return df
    except: return None

df = load_data(DATABASE_FILE) if os.path.exists(DATABASE_FILE) else None

if df is not None:
    st.markdown('<div class="main-title">🍀 Mitoloto</div>', unsafe_allow_html=True)

    if 'wybrane' not in st.session_state:
        st.session_state.wybrane = set()

    # --- GENEROWANIE SIATKI ---
    for r in range(7):
        cols = st.columns(7)
        for c in range(7):
            num = r * 7 + c + 1
            with cols[c]:
                is_sel = num in st.session_state.wybrane
                # Krótki label, żeby nie rozpychał przycisku
                label = f"X{num}" if is_sel else str(num)
                if st.button(label, key=f"b_{num}"):
                    if num in st.session_state.wybrane:
                        st.session_state.wybrane.remove(num)
                    elif len(st.session_state.wybrane) < 12:
                        st.session_state.wybrane.add(num)
                    st.rerun()

    wybrane_lista = sorted(list(st.session_state.wybrane))
    
    st.write(f"Suma: **{len(wybrane_lista)}/12**")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("RESET", use_container_width=True):
            st.session_state.wybrane = set(); st.rerun()
    with c2:
        if st.button("LOSUJ", use_container_width=True):
            import random
            st.session_state.wybrane = set(random.sample(range(1, 50), 6)); st.rerun()

    if 6 <= len(wybrane_lista) <= 12:
        if st.button("🚀 ANALIZUJ", type="primary", use_container_width=True):
            n = len(wybrane_lista); set_wybrane = set(wybrane_lista)
            komb = math.comb(n, 6)
            staty = {6:0, 5:0, 4:0, 3:0}; bilans = 0; historia = []
            
            for _, row in df.iterrows():
                traf = len(set_wybrane.intersection({row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}))
                w_los = 0
                if traf >= 3:
                    w_los += (math.comb(traf, 3) * math.comb(n-traf, 3)) * 24
                    w_los += (math.comb(traf, 4) * math.comb(n-traf, 2)) * 170
                    w_los += (math.comb(traf, 5) * math.comb(n-traf, 1)) * 5000
                    w_los += (math.comb(traf, 6) * math.comb(n-traf, 0)) * 2000000
                    for d in [3,4,5,6]:
                        if traf >= d: staty[d] += math.comb(traf, d) * math.comb(n-traf, 6-d)
                bilans += (w_los - (komb * 3))
                historia.append(bilans)

            st.metric("SALDO", f"{bilans:,} zł")
            fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='#FF4B4B')))
            fig.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.table(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Suma": [staty[6], staty[5], staty[4], staty[3]]}))
else:
    st.error("Baza danych nieobecna.")
