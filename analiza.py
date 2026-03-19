import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")


st.markdown("""
    <style>
    /* Stylizacja kontenera przycisków */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 45px;
        padding: 0;
        font-weight: bold;
    }
    /* Kolor dla zaznaczonych liczb (symulacja) */
    .selected-btn {
        background-color: #28a745 !important;
        color: white !important;
    }
    /* Układ siatki dla mobile */
    div[data-testid="column"] {
        padding: 1px !important;
        min-width: 40px !important;
    }
    </style>
    """, unsafe_allow_html=True)

DATABASE_FILE = "wyniki.csv"

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
    st.title("🎰 Twój Kupon")
    
    # Inicjalizacja stanu wybranych liczb
    if 'wybrane' not in st.session_state:
        st.session_state.wybrane = set()

    # --- RENDEROWANIE KUPONU 7x7 ---
    for r in range(7):
        cols = st.columns(7)
        for c in range(7):
            num = r * 7 + c + 1
            with cols[c]:
                # Sprawdzamy czy liczba jest wybrana, żeby zmienić styl (uproszczone)
                is_selected = num in st.session_state.wybrane
                label = f"X {num}" if is_selected else str(num)
                
                if st.button(label, key=f"btn_{num}", use_container_width=True):
                    if num in st.session_state.wybrane:
                        st.session_state.wybrane.remove(num)
                    elif len(st.session_state.wybrane) < 12:
                        st.session_state.wybrane.add(num)
                    st.rerun()

    wybrane_lista = sorted(list(st.session_state.wybrane))
    st.write(f"Wybrano ({len(wybrane_lista)}/12): **{', '.join(map(str, wybrane_lista))}**")

    if st.button("WYCZYŚĆ KUPON"):
        st.session_state.wybrane = set()
        st.rerun()

    with st.sidebar:
        st.header("Opcje")
        min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
        zakres = st.slider("Lata:", min_r, max_r, (min_r, max_r))
        if st.file_uploader("Nowa baza", type=['csv']): st.rerun()

    if 6 <= len(wybrane_lista) <= 12:
        if st.button("📊 ANALIZUJ", type="primary", use_container_width=True):
            n = len(wybrane_lista)
            komb = math.comb(n, 6)
            dane_f = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])].copy()
            
            staty = {6:0, 5:0, 4:0, 3:0}
            bilans = 0
            historia = []
            
            for _, row in dane_f.iterrows():
                traf = len(set(wybrane_lista).intersection({row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}))
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
            
            # Wykres Cashflow (uproszczony pod mobile)
            fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy'))
            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(pd.DataFrame({"Traf": ["6/6","5/6","4/6","3/6"], "Suma": [staty[6], staty[5], staty[4], staty[3]]}), use_container_width=True)
    else:
        st.warning("Zaznacz min. 6 liczb na kuponie.")
else:
    st.error("Wgraj wyniki.csv")