import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- KOD CSS WYMUSZAJĄCY SZTYWNY UKŁAD 7 KOLUMN ---
st.markdown("""
    <style>
    /* Usuwamy marginesy głównego kontenera */
    .block-container {
        padding: 1rem 0.5rem !important;
    }
    
    /* KLUCZ: Wymuszenie rzędu bez zawijania (no-wrap) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 2px !important;
    }

    /* KLUCZ: Każda kolumna musi mieć 1/7 szerokości i ZERO minimalnej szerokości */
    [data-testid="column"] {
        width: 14% !important;
        min-width: 0px !important; 
        flex: 1 1 auto !important;
    }

    /* Przycisk: kwadratowy i ciasny */
    .stButton > button {
        width: 100% !important;
        height: 40px !important;
        padding: 0px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border: 1px solid #ccc !important;
        border-radius: 4px !important;
    }
    
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 5px;
    }
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

    # --- KUPON (SIATKA) ---
    for r in range(7):
        # gap="none" dodatkowo pomaga w nowszych wersjach Streamlit
        cols = st.columns(7)
        for c in range(7):
            num = r * 7 + c + 1
            with cols[c]:
                is_sel = num in st.session_state.wybrane
                label = f"●{num}" if is_sel else str(num)
                if st.button(label, key=f"b_{num}"):
                    if num in st.session_state.wybrane:
                        st.session_state.wybrane.remove(num)
                    elif len(st.session_state.wybrane) < 12:
                        st.session_state.wybrane.add(num)
                    st.rerun()

    wybrane_lista = sorted(list(st.session_state.wybrane))
    st.write(f"Wybrane ({len(wybrane_lista)}): **{', '.join(map(str, wybrane_lista))}**")
    
    if st.button("RESETUJ KUPON", use_container_width=True):
        st.session_state.wybrane = set()
        st.rerun()

    with st.sidebar:
        st.header("Mitoloto Opcje")
        min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
        zakres = st.slider("Lata:", min_r, max_r, (min_r, max_r))

    if 6 <= len(wybrane_lista) <= 12:
        if st.button("📊 ANALIZUJ", type="primary", use_container_width=True):
            n = len(wybrane_lista)
            komb = math.comb(n, 6)
            dane_f = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])]
            
            staty = {6:0, 5:0, 4:0, 3:0}
            bilans = 0
            historia = []
            set_wybrane = set(wybrane_lista)

            for _, row in dane_f.iterrows():
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

            st.metric("CASHFLOW", f"{bilans:,} zł")
            fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='#FF4B4B')))
            fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.table(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Suma": [staty[6], staty[5], staty[4], staty[3]]}))
else:
    st.error("Błąd: Wgraj plik wyniki.csv do repozytorium.")