import streamlit as st
import pandas as pd
import math
import os

st.set_page_config(page_title="ANALIzator 6000", layout="wide")

DATABASE_FILE = "wyniki.csv"

st.title("🎰 ANALIzator 6000")

# Funkcja do wczytywania danych
def load_data(source):
    try:
        if hasattr(source, 'getvalue'):
            first_line = source.getvalue().decode('utf-8').splitlines()[0]
            source.seek(0)
        else: # Jeśli to plik lokalny (z GitHuba)
            with open(source, 'r', encoding='utf-8') as f:
                first_line = f.readline()
        
        sep = ';' if ';' in first_line else '\t' if '\t' in first_line else ','
        
        df = pd.read_csv(source, sep=sep, header=None, 
                         names=['Nr', 'Data', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'])
        

        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data'])
        df['Rok'] = df['Data'].dt.year
        return df
    except Exception as e:
        st.error(f"Błąd formatu pliku: {e}")
        return None


df = None

if os.path.exists(DATABASE_FILE):

    df = load_data(DATABASE_FILE)
    st.sidebar.success("✅ Załadowano bazę `wyniki.csv` z serwera.")
else:

    st.sidebar.warning("⚠️ Nie znaleziono `wyniki.csv` na serwerze.")
    manual_file = st.sidebar.file_uploader("Wgraj plik wyniki.csv ręcznie:", type=['csv'])
    if manual_file:
        df = load_data(manual_file)

# --- RESZTA APLIKACJI ---
if df is not None:

    wybrane = st.multiselect("Wybierz system (6-12 liczb):", 
                              options=list(range(1, 50)), 
                              max_selections=12)


    min_r, max_r = int(df['Rok'].min()), int(df['Rok'].max())
    zakres = st.slider("Lata:", min_r, max_r, (min_r, max_r))

    if len(wybrane) >= 6:
        n = len(wybrane)
        kombinacje = math.comb(n, 6)
        
        if st.button("ANALIZUJ", type="primary"):
            dane_filtr = df[(df['Rok'] >= zakres[0]) & (df['Rok'] <= zakres[1])]
            
            total_losowan = len(dane_filtr)
            set_wybrane = set(wybrane)
            staty = {6: 0, 5: 0, 4: 0, 3: 0}
            
            for _, row in dane_filtr.iterrows():
                wylosowane = {row['L1'], row['L2'], row['L3'], row['L4'], row['L5'], row['L6']}
                k = len(set_wybrane.intersection(wylosowane))
                
                if k >= 3:
                    if k >= 6: staty[6] += math.comb(k, 6) * math.comb(n-k, 0)
                    if k >= 5: staty[5] += math.comb(k, 5) * math.comb(n-k, 1)
                    if k >= 4: staty[4] += math.comb(k, 4) * math.comb(n-k, 2)
                    if k >= 3: staty[3] += math.comb(k, 3) * math.comb(n-k, 3)


            koszt = total_losowan * kombinacje * 3
            wygrana = (staty[3]*24) + (staty[4]*170) + (staty[5]*5000) + (staty[6]*2000000)
            bilans = wygrana - koszt

            c1, c2, c3 = st.columns(3)
            c1.metric("Wygrane", f"{wygrana:,} zł")
            c2.metric("Koszt", f"{koszt:,} zł", delta=f"-{koszt:,}", delta_color="inverse")
            c3.metric("BILANS", f"{bilans:,} zł", delta=f"{bilans:,}")
            
            st.table(pd.DataFrame({"Stopień": ["6", "5", "4", "3"], "Trafienia": [staty[6], staty[5], staty[4], staty[3]]}))
else:
    st.info("Czekam na dane... Upewnij się, że plik `wyniki.csv` znajduje się w Twoim repozytorium na GitHub.")