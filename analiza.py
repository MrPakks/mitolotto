import streamlit as st
import pandas as pd
import math
import os

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
            dane_filtr = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])]
            total_losowan = len(dane_filtr)
            set_wybrane = set(wybrane)
            staty = {6: 0, 5: 0, 4: 0, 3: 0}
            szczegoly = []

            for _, row in dane_filtr.iterrows():
                wylosowane = {row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}
                k = len(set_wybrane.intersection(wylosowane))
                if k >= 3:
                    if k >= 6: staty[6] += math.comb(k, 6) * math.comb(n-k, 0)
                    if k >= 5: staty[5] += math.comb(k, 5) * math.comb(n-k, 1)
                    if k >= 4: staty[4] += math.comb(k, 4) * math.comb(n-k, 2)
                    if k >= 3: staty[3] += math.comb(k, 3) * math.comb(n-k, 3)
                    if k >= 5:
                        txt = "SZÓSTKA!" if k == 6 else "Piątka"
                        szczegoly.append(f"{txt}: Losowanie {row['Nr']} ({row['Data'].strftime('%d.%m.%Y')})")

            koszt = total_losowan * kombinacje * 3
            wygrana = (staty[3]*24) + (staty[4]*170) + (staty[5]*5000) + (staty[6]*2000000)
            bilans = wygrana - koszt

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Wygrane", f"{wygrana:,} zł")
            c2.metric("Koszt", f"{koszt:,} zł", delta=f"-{koszt:,}", delta_color="inverse")
            c3.metric("BILANS", f"{bilans:,} zł", delta=f"{bilans:,}")
            
            st.table(pd.DataFrame({
                "Stopień": ["6/6", "5/6", "4/6", "3/6"],
                "Ilość": [staty[6], staty[5], staty[4], staty[3]]
            }))

            if szczegoly:
                with st.expander("Szczegóły wysokich trafień"):
                    for s in szczegoly: st.write(s)
    elif ile > 12:
        st.error("Max 12 liczb!")
else:
    st.info("Wgraj wyniki.csv do repozytorium.")