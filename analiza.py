import streamlit as st
import pandas as pd
import math
import os
import plotly.graph_objects as go

st.set_page_config(page_title="ANALIzator 6000", layout="wide")

DATABASE_FILE = "wyniki.csv"

def load_data(source):
    try:
        if hasattr(source, 'getvalue'): 
            first_line = source.getvalue().decode('utf-8').splitlines()[0]
            source.seek(0)
        else:
            with open(source, 'r', encoding='utf-8') as f:
                first_line = f.readline()
        
        sep = ';' if ';' in first_line else '\t' if '\t' in first_line else ','
        df = pd.read_csv(source, sep=sep, header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data'])
        df = df.sort_values('Data')
        df['Rok'] = df['Data'].dt.year
        return df
    except:
        return None

df = None
if os.path.exists(DATABASE_FILE):
    df = load_data(DATABASE_FILE)
else:
    manual_file = st.sidebar.file_uploader("Wgraj wyniki.csv", type=['csv'])
    if manual_file:
        df = load_data(manual_file)

if df is not None:
    st.subheader("Skreśl od 6 do 12 liczb:")
    cols = st.columns(7)
    wybrane = []

    for i in range(1, 50):
        col_idx = (i - 1) % 7
        with cols[col_idx]:
            if st.checkbox(f"{i}", key=f"n_{i}"):
                wybrane.append(i)

    ile = len(wybrane)
    st.markdown(f"### Zaznaczono: `{ile}/12`")

    min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
    zakres = st.sidebar.slider("Lata:", min_r, max_r, (min_r, max_r))

    if 6 <= ile <= 12:
        if st.button("ANALIZUJ", type="primary"):
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
                
                wygrana_losowania = 0
                if k >= 3:
                    wygrana_losowania += (math.comb(k, 3) * math.comb(n-k, 3)) * 24
                    wygrana_losowania += (math.comb(k, 4) * math.comb(n-k, 2)) * 170
                    wygrana_losowania += (math.comb(k, 5) * math.comb(n-k, 1)) * 5000
                    wygrana_losowania += (math.comb(k, 6) * math.comb(n-k, 0)) * 2000000
                    
                    if k >= 3:
                        staty[3] += math.comb(k, 3) * math.comb(n-k, 3)
                    if k >= 4:
                        staty[4] += math.comb(k, 4) * math.comb(n-k, 2)
                    if k >= 5:
                        staty[5] += math.comb(k, 5) * math.comb(n-k, 1)
                    if k >= 6:
                        staty[6] += math.comb(k, 6) * math.comb(n-k, 0)

                koszt_losowania = kombinacje * 3
                biezacy_bilans += (wygrana_losowania - koszt_losowania)
                
                historia_bilansu.append(biezacy_bilans)
                daty_wykresu.append(row['Data'])

            st.divider()
            total_wygrana = sum(v * amt for v, amt in zip([staty[3], staty[4], staty[5], staty[6]], [24, 170, 5000, 2000000]))
            total_koszt = len(dane_filtr) * kombinacje * 3
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Suma wygranych", f"{total_wygrana:,} zł")
            c2.metric("Koszt całkowity", f"{total_koszt:,} zł", delta_color="inverse")
            c3.metric("Bilans końcowy", f"{biezacy_bilans:,} zł")

            st.subheader("Wykres Cashflow (Narastająco)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daty_wykresu, y=historia_bilansu, mode='lines', name='Bilans', line=dict(color='#28a745' if biezacy_bilans > 0 else '#dc3545')))
            fig.update_layout(xaxis_title="Data", yaxis_title="PLN", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.table(pd.DataFrame({"Stopień": ["6/6", "5/6", "4/6", "3/6"], "Ilość": [staty[6], staty[5], staty[4], staty[3]]}))
    elif ile > 12:
        st.error("Max 12 liczb!")
else:
    st.info("Wgraj wyniki.csv do repozytorium.")