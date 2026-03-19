import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- INITIAL STATE ---
if 'wybrane' not in st.session_state:
    st.session_state.wybrane = set()

# Zmienna pomocnicza na wypadek, gdyby df nie istniał
wybrane_lista = sorted(list(st.session_state.wybrane))

# --- DYNAMICZNY CSS DLA KOLORÓW I WYŚRODKOWANIA ---
selected_css_rules = ""
for num in st.session_state.wybrane:
    # Obliczamy pozycję w siatce (zakładając, że kupon to pierwsze rzędy bloków)
    row_idx = (num - 1) // 7 + 2 
    col_idx = (num - 1) % 7 + 1
    selected_css_rules += f"""
    div[data-testid="stVerticalBlock"] > div:nth-child({row_idx}) div[data-testid="column"]:nth-child({col_idx}) button {{
        background-color: #008000 !important;
        color: white !important;
        border: 2px solid #00ff00 !important;
        box-shadow: 0 0 8px #00ff00;
    }}
    """

st.markdown(f"""
<style>
    div.stHorizontalBlock {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        margin-bottom: -10px !important;
    }}
    div.stHorizontalBlock > div {{
        width: 14% !important;
        min-width: 0px !important;
        flex-basis: 14% !important;
        padding: 0px !important;
    }}
    div.stButton > button {{
        width: 100% !important;
        height: 42px !important;
        font-size: 15px !important;
        font-family: 'Courier New', Courier, monospace !important;
        background-color: #1e1e1e !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        white-space: pre !important; /* Ważne, żeby spacje nie znikały */
    }}
    {selected_css_rules}
    .main-title {{ text-align: center; color: #FF4B4B; font-size: 32px; font-weight: 900; }}
</style>
""", unsafe_allow_html=True)

# --- ŁADOWANIE DANYCH ---
DATABASE_FILE = "wyniki.csv"

@st.cache_data
def load_data(source):
    if not os.path.exists(source):
        return None
    try:
        df = pd.read_csv(source, sep=None, engine='python', header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['Data']).sort_values('Data')
    except:
        return None

df = load_data(DATABASE_FILE)

st.markdown("<div class='main-title'>🍀 Mitoloto</div>", unsafe_allow_html=True)

# --- SIATKA KUPONU ---
for r in range(7):
    cols = st.columns(7)
    for c in range(7):
        num = r * 7 + c + 1
        # Twoja prośba o spacje: 2 przed/po dla 1-cyfrowych, 1 przed/po dla 2-cyfrowych
        label = f"  {num}  " if num < 10 else f" {num} "
        
        with cols[c]:
            if st.button(label, key=f"btn_{num}"):
                if num in st.session_state.wybrane:
                    st.session_state.wybrane.remove(num)
                elif len(st.session_state.wybrane) < 12:
                    st.session_state.wybrane.add(num)
                st.rerun()

# Aktualizacja listy po kliknięciach
wybrane_lista = sorted(list(st.session_state.wybrane))
st.write(f"Wybrane ({len(wybrane_lista)}/12): **{', '.join(map(str, wybrane_lista))}**")

# --- AKCJE ---
c1, c2 = st.columns(2)
with c1:
    if st.button("RESET", use_container_width=True):
        st.session_state.wybrane = set()
        st.rerun()
with c2:
    if st.button("LOSUJ 6", use_container_width=True):
        import random
        st.session_state.wybrane = set(random.sample(range(1, 50), 6))
        st.rerun()

# --- ANALIZA (Zabezpieczona przed NameError) ---
if 6 <= len(wybrane_lista) <= 12:
    if df is not None:
        if st.button("🚀 ANALIZUJ", type="primary", use_container_width=True):
            n = len(wybrane_lista)
            set_wybrane = set(wybrane_lista)
            komb = math.comb(n, 6)
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
            st.table(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Suma": [staty[6], staty[5], staty[4], staty[3]]}))
    else:
        st.error("⚠️ Błąd: Nie znaleziono pliku
