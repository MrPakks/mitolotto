import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- WYMUSZENIE SIATKI NA MOBILE (CSS) ---
st.markdown("""
    <style>
    /* Wymuszamy, aby kontenery kolumn nie przeskakiwały do pionu */
    [data-testid="column"] {
        flex: 1 1 14% !important; /* 100% / 7 kolumn = ~14% */
        min-width: 14% !important;
        max-width: 14% !important;
    }
    /* Styl przycisków */
    .stButton > button {
        width: 100%;
        height: 40px;
        padding: 0px;
        font-size: 14px;
        margin-bottom: -10px;
    }
    /* Ukrycie odstępów między elementami */
    [data-testid="stVerticalBlock"] > div {
        gap: 0.1rem !important;
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
    st.title("🎰 Kupon Mobile")
    
    if 'wybrane' not in st.session_state:
        st.session_state.wybrane = set()

    # --- KUPON 7x7 ---
    for r in range(7):
        cols = st.columns(7)
        for c in range(7):
            num = r * 7 + c + 1
            with cols[c]:
                is_sel = num in st.session_state.wybrane
                # Używamy emoji lub tekstu do oznaczenia wyboru
                label = f"📍{num}" if is_sel else str(num)
                
                if st.button(label, key=f"b_{num}"):
                    if num in st.session_state.wybrane:
                        st.session_state.wybrane.remove(num)
                    elif len(st.session_state.wybrane) < 12:
                        st.session_state.wybrane.add(num)
                    st.rerun()

    wybrane_lista = sorted(list(st.session_state.wybrane))
    
    col_info1, col_info2 = st.columns([2,1])
    col_info1.write(f"Wybrane: **{', '.join(map(str, wybrane_lista))}**")
    if col_info2.button("RESET"):
        st.session_state.wybrane = set()
        st.rerun()

    # Filtry w sidebarze
    with st.sidebar:
        min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
        zakres = st.slider("Lata:", min_r, max_r, (min_r, max_r))

    if 6 <= len(wybrane_lista) <= 12:
        if st.button("📊 ANALIZUJ", type="primary", use_container_width=True):
            n = len(wybrane_lista)
            komb = math.comb(n, 6)
            dane_f = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])].copy()
            
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
            
            fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='green')))
            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.table(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Ilość": [staty[6], staty[5], staty[4], staty[3]]}))
    else:
        st.info("Zaznacz min. 6 liczb")
else:
    st.error("Brak pliku wyniki.csv")