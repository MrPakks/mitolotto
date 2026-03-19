import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- ZAAWANSOWANY CSS DLA KOLORÓW ---
st.markdown("""
<style>
    /* Wymuszenie rzędu 7 kolumn */
    div.stHorizontalBlock {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    div.stHorizontalBlock > div {
        width: 14% !important;
        min-width: 0px !important;
        flex-basis: 14% !important;
    }
    
    /* Podstawowy styl przycisku */
    button {
        width: 100% !important;
        height: 42px !important;
        padding: 0px !important;
        font-size: 13px !important;
        background-color: #262730 !important; /* Ciemne tło pasujące do trybu dark */
        color: white !important;
        border: 1px solid #444 !important;
        transition: 0.3s;
    }

    /* MAGICZNY TRIK: Styl dla przycisku zawierającego kropkę (zaznaczonego) */
    /* Używamy selektora, który szuka tekstu wewnątrz guzika */
    div[data-testid="stHorizontalBlock"] button p:contains("●") {
        color: #00ff00 !important; /* Jasnozielony tekst */
    }
    
    /* Alternatywne podejście dla nowszych wersji - celujemy w cały przycisk */
    /* Jeśli przycisk ma kropkę, zmieniamy mu tło na ciemnozielone */
    button:has(p:contains("●")) {
        background-color: #004d00 !important; 
        border: 1px solid #00ff00 !important;
    }

    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 32px;
        font-weight: 900;
        margin-top: -30px;
    }
</style>
""", unsafe_allow_html=True)

# --- ŁADOWANIE DANYCH ---
DATABASE_FILE = "wyniki.csv"

@st.cache_data
def load_data(source):
    try:
        df = pd.read_csv(source, sep=None, engine='python', header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data']).sort_values('Data')
        return df
    except: return None

df = load_data(DATABASE_FILE) if os.path.exists(DATABASE_FILE) else None

# --- STATE ---
if 'wybrane' not in st.session_state:
    st.session_state.wybrane = set()

st.markdown("<div class='main-title'>🍀 Mitoloto</div>", unsafe_allow_html=True)

# --- RYSOWANIE ---
for r in range(7):
    cols = st.columns(7)
    for c in range(7):
        num = r * 7 + c + 1
        with cols[c]:
            is_sel = num in st.session_state.wybrane
            label = f"●{num}" if is_sel else str(num)
            if st.button(label, key=f"n_{num}"):
                if num in st.session_state.wybrane:
                    st.session_state.wybrane.remove(num)
                elif len(st.session_state.wybrane) < 12:
                    st.session_state.wybrane.add(num)
                st.rerun()

wybrane_lista = sorted(list(st.session_state.wybrane))
st.write(f"Wybrane ({len(wybrane_lista)}): **{', '.join(map(str, wybrane_lista))}**")

# --- PRZYCISKI AKCJI ---
c1, c2 = st.columns(2)
with c1:
    if st.button("WYCZYŚĆ", use_container_width=True):
        st.session_state.wybrane = set()
        st.rerun()
with c2:
    if st.button("LOSUJ 6", use_container_width=True):
        import random
        st.session_state.wybrane = set(random.sample(range(1, 50), 6))
        st.rerun()

# --- ANALIZA ---
if 6 <= len(wybrane_lista) <= 12 and df is not None:
    if st.button("🚀 ANALIZUJ HISTORIĘ", type="primary", use_container_width=True):
        n = len(wybrane_lista)
        komb = math.comb(n, 6)
        set_wybrane = set(wybrane_lista)
        staty = {6:0, 5:0, 4:0, 3:0}
        bilans = 0
        historia = []
        
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
        
        st.metric("BILANS FINALNY", f"{bilans:,} zł")
        fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='#00ff00')))
        fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.table(pd.DataFrame({"Trafienie": ["6/6","5/6","4/6","3/6"], "Suma": [staty[6], staty[5], staty[4], staty[3]]}))

elif df is None:
    st.error("Wgraj wyniki.csv!")
