import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- DATABASE ---
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

# --- LOGIKA WYBORU ---
if 'wybrane' not in st.session_state:
    st.session_state.wybrane = set()

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🍀 Mitoloto</h1>", unsafe_allow_html=True)

# Budujemy kupon ręcznie, używając przycisków Streamlit w kontenerze HTML
# ale żeby nie spadały, musimy użyć st.write z unikalnym CSS

st.markdown("""
<style>
    /* Ta sekcja wymusza na kontenerze, żeby nie zawijał dzieci do nowej linii */
    div.stHorizontalBlock {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 2px !important;
    }
    div.stHorizontalBlock > div {
        width: 14% !important;
        min-width: 0px !important;
        flex-basis: 14% !important;
    }
    button {
        width: 100% !important;
        height: 40px !important;
        padding: 0px !important;
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)

# RYSOWANIE KUPONU
for r in range(7):
    cols = st.columns(7)
    for c in range(7):
        num = r * 7 + c + 1
        with cols[c]:
            is_sel = num in st.session_state.wybrane
            label = f"X{num}" if is_sel else str(num)
            if st.button(label, key=f"n_{num}"):
                if num in st.session_state.wybrane:
                    st.session_state.wybrane.remove(num)
                elif len(st.session_state.wybrane) < 12:
                    st.session_state.wybrane.add(num)
                st.rerun()

wybrane_lista = sorted(list(st.session_state.wybrane))
st.write(f"Wybrano: {', '.join(map(str, wybrane_lista))}")

# PRZYCISKI AKCJI
col1, col2 = st.columns(2)
with col1:
    if st.button("RESET", use_container_width=True):
        st.session_state.wybrane = set()
        st.rerun()
with col2:
    if st.button("LOSUJ", use_container_width=True):
        import random
        st.session_state.wybrane = set(random.sample(range(1, 50), 6))
        st.rerun()

# --- ANALIZA ---
if 6 <= len(wybrane_lista) <= 12 and df is not None:
    if st.button("🚀 ANALIZUJ", type="primary", use_container_width=True):
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
        
        st.metric("SALDO FINALNE", f"{bilans:,} zł")
        fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='#FF4B4B')))
        fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.table(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Ilość": [staty[6], staty[5], staty[4], staty[3]]}))

elif df is None:
    st.error("Wgraj wyniki.csv na GitHub!")
