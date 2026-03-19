import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="Mitoloto", layout="centered")

# --- CLEAN UI CSS ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 32px;
        font-weight: 900;
        margin-bottom: 20px;
    }
    .stNumberInput, .stTextInput {
        margin-bottom: 10px;
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

    # --- WPISYWANIE LICZB ---
    st.write("Wpisz swoje liczby (od 6 do 12 liczb, oddzielone spacją lub przecinkiem):")
    input_liczb = st.text_input("Twoje liczby:", placeholder="np. 1, 12, 23, 34, 45, 49")
    
    # Procesowanie wpisanych danych
    wybrane = []
    if input_liczb:
        # Zamiana przecinków na spacje i rozbicie tekstu
        raw_numbers = input_liczb.replace(',', ' ').split()
        try:
            # Konwersja na int, filtrowanie zakresu 1-49 i usuwanie duplikatów
            wybrane = sorted(list(set([int(n) for n in raw_numbers if 1 <= int(n) <= 49])))
        except ValueError:
            st.error("Wpisz tylko liczby!")

    # Wyświetlanie aktualnego stanu
    if wybrane:
        st.success(f"Wybrano {len(wybrane)} liczb: **{', '.join(map(str, wybrane))}**")
    
    with st.sidebar:
        st.header("Opcje")
        min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
        zakres = st.slider("Zakres lat:", min_r, max_r, (min_r, max_r))

    # --- ANALIZA ---
    if 6 <= len(wybrane) <= 12:
        if st.button("🚀 ANALIZUJ SYSTEM", type="primary", use_container_width=True):
            n = len(wybrane)
            komb = math.comb(n, 6)
            dane_f = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])].copy()
            
            staty = {6:0, 5:0, 4:0, 3:0}
            bilans = 0
            historia = []
            set_wybrane = set(wybrane)

            for _, row in dane_f.iterrows():
                wylosowane = {row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}
                traf = len(set_wybrane.intersection(wylosowane))
                
                w_los = 0
                if traf >= 3:
                    # Obliczanie trafień systemowych
                    w_los += (math.comb(traf, 3) * math.comb(n-traf, 3)) * 24
                    w_los += (math.comb(traf, 4) * math.comb(n-traf, 2)) * 170
                    w_los += (math.comb(traf, 5) * math.comb(n-traf, 1)) * 5000
                    w_los += (math.comb(traf, 6) * math.comb(n-traf, 0)) * 2000000
                    
                    for d in [3,4,5,6]:
                        if traf >= d:
                            staty[d] += math.comb(traf, d) * math.comb(n-traf, 6-d)

                bilans += (w_los - (komb * 3))
                historia.append(bilans)

            # Wyniki
            st.divider()
            st.metric("SALDO FINALNE", f"{bilans:,} zł")
            
            fig = go.Figure(go.Scatter(y=historia, mode='lines', fill='tozeroy', line=dict(color='#FF4B4B')))
            fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            res_df = pd.DataFrame({
                "Trafienie": ["6/6", "5/6", "4/6", "3/6"],
                "Ilość": [staty[6], staty[5], staty[4], staty[3]]
            })
            st.table(res_df)
    elif len(wybrane) > 12:
        st.error("System Lotto obsługuje max 12 liczb!")
    elif input_liczb:
        st.warning("Musisz podać przynajmniej 6 liczb.")

else:
    st.error("Błąd: Brak pliku wyniki.csv w repozytorium GitHub.")
