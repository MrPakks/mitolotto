import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

# Konfiguracja strony - wymuszamy szeroki układ
st.set_page_config(page_title="Mitoloto", layout="wide", initial_sidebar_state="collapsed")

# Stylowanie CSS dla lepszego wyglądu przycisków na telefonie
st.markdown("""
    <style>
    [data-testid="stCheckbox"] {
        background-color: #f0f2f6;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin-bottom: 2px;
        text-align: center;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

DATABASE_FILE = "wyniki.csv"

def load_data(source):
    try:
        sep = ';'
        df = pd.read_csv(source, sep=None, engine='python', header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data']).sort_values('Data')
        df['Rok'] = df['Data'].dt.year
        return df
    except:
        return None

df = load_data(DATABASE_FILE) if os.path.exists(DATABASE_FILE) else None

if df is not None:
    st.title("📱 Mobilny ANALIzator")
    
    # Sekcja Wyboru - Siatka 7-kolumnowa
    st.write("### Skreśl liczby:")
    
    # Używamy kontenera, aby przyciski były blisko siebie
    wybrane = []
    rows = [st.columns(7) for _ in range(7)]
    for i in range(1, 50):
        row_idx = (i - 1) // 7
        col_idx = (i - 1) % 7
        with rows[row_idx][col_idx]:
            if st.checkbox(f"{i}", key=f"m_{i}", label_visibility="visible"):
                wybrane.append(i)

    ile = len(wybrane)
    st.info(f"Zaznaczono: **{ile}/12**")

    # Filtry lądują w sidebarze, żeby nie zajmować miejsca na ekranie głównym
    with st.sidebar:
        st.header("Ustawienia")
        min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
        zakres = st.slider("Lata:", min_r, max_r, (min_r, max_r))
        st.write("---")
        st.write("Wgraj nową bazę:")
        manual_file = st.file_uploader("", type=['csv'])
        if manual_file:
            df = load_data(manual_file)

    if 6 <= ile <= 12:
        if st.button("🚀 OBLICZ WYNIKI", use_container_width=True, type="primary"):
            n = ile
            kombinacje = math.comb(n, 6)
            dane_filtr = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])].copy()
            
            set_wybrane = set(wybrane)
            staty = {6: 0, 5: 0, 4: 0, 3: 0}
            biezacy_bilans = 0
            historia_bilansu = []
            daty_wykresu = []

            for _, row in dane_filtr.iterrows():
                wylosowane = {row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}
                k = len(set_wybrane.intersection(wylosowane))
                
                wygrana_l = 0
                if k >= 3:
                    wygrana_l += (math.comb(k, 3) * math.comb(n-k, 3)) * 24
                    wygrana_l += (math.comb(k, 4) * math.comb(n-k, 2)) * 170
                    wygrana_l += (math.comb(k, 5) * math.comb(n-k, 1)) * 5000
                    wygrana_l += (math.comb(k, 6) * math.comb(n-k, 0)) * 2000000
                    
                    for deg in [3, 4, 5, 6]:
                        if k >= deg:
                            staty[deg] += math.comb(k, deg) * math.comb(n-k, 6-deg)

                biezacy_bilans += (wygrana_l - (kombinacje * 3))
                historia_bilansu.append(biezacy_bilans)
                daty_wykresu.append(row['Data'])

            # Wyniki w pionie dla mobile
            st.metric("BILANS FINALNY", f"{biezacy_bilans:,} zł")
            
            col_a, col_b = st.columns(2)
            total_wygrana = sum(v * amt for v, amt in zip([staty[3], staty[4], staty[5], staty[6]], [24, 170, 5000, 2000000]))
            col_a.metric("Wygrane", f"{total_wygrana:,} zł")
            col_b.metric("Koszt", f"{(len(dane_filtr)*kombinacje*3):,} zł")

            # Wykres Cashflow
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daty_wykresu, y=historia_bilansu, fill='tozeroy', name='Bilans'))
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # Tabela trafień (uproszczona)
            st.dataframe(pd.DataFrame({
                "Trafienie": ["6/6", "5/6", "4/6", "3/6"],
                "Suma": [staty[6], staty[5], staty[4], staty[3]]
            }), use_container_width=True)
    else:
        st.warning("Wybierz 6-12 liczb.")
else:
    st.error("Brak pliku wyniki.csv! Wgraj go na GitHub.")