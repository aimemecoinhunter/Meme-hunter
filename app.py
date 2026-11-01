import streamlit as st
import pandas as pd
from gecko import fetch_new_pools
from scoring import score_pool

st.set_page_config(page_title="AI Meme Coin Hunter", page_icon="🎯", layout="wide")
st.title("🎯 AI Meme Coin Hunter")
st.caption("Solana meme-coin discovery scanner • GeckoTerminal • Research only, no trading")

with st.sidebar:
    st.header("Filtre")
    min_liquidity = st.number_input("Lichiditate minimă (USD)", min_value=0, value=10000, step=1000)
    min_volume = st.number_input("Volum 1h minim (USD)", min_value=0, value=1000, step=500)
    max_age = st.number_input("Vechime maximă (ore)", min_value=1, value=72, step=1)
    limit = st.slider("Număr de pool-uri analizate", 10, 100, 50, 10)
    run = st.button("🔎 Scanează Solana", type="primary", use_container_width=True)

st.info("Apasă «Scanează Solana» pentru a prelua cele mai noi pool-uri. Datele provin de la GeckoTerminal și pot avea întârzieri sau lipsuri.")

if run:
    with st.spinner("Preiau și analizez pool-urile Solana..."):
        try:
            raw = fetch_new_pools(limit=limit)
            rows = []
            for item in raw:
                row = score_pool(item)
                if row:
                    rows.append(row)
            df = pd.DataFrame(rows)
            if df.empty:
                st.warning("Nu am găsit date suficiente. Încearcă din nou peste câteva minute.")
            else:
                df = df[
                    (df["Lichiditate USD"] >= min_liquidity) &
                    (df["Volum 1h USD"] >= min_volume) &
                    (df["Vechime ore"] <= max_age)
                ].sort_values("Scor", ascending=False)
                st.session_state["results"] = df
        except Exception as e:
            st.error(f"Scanarea nu a reușit: {e}")

if "results" in st.session_state:
    df = st.session_state["results"]
    a, b, c = st.columns(3)
    a.metric("Monede/pool-uri eligibile", len(df))
    b.metric("Scor maxim", int(df["Scor"].max()) if len(df) else "—")
    c.metric("Lichiditate mediană", f"${df['Lichiditate USD'].median():,.0f}" if len(df) else "—")
    st.subheader("Clasament")
    if len(df):
        st.dataframe(
            df[["Token", "Scor", "Lichiditate USD", "Volum 1h USD", "Vechime ore", "Explicație", "DEX Screener"]],
            use_container_width=True, hide_index=True,
            column_config={"DEX Screener": st.column_config.LinkColumn("DEX Screener")}
        )
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Descarcă rezultatele CSV", csv, "solana_meme_coin_scan.csv", "text/csv")
    else:
        st.warning("Niciun pool nu respectă filtrele. Redu pragurile din bara laterală.")
else:
    st.markdown("### Cum funcționează")
    st.markdown("""
    1. Preia pool-uri noi de pe Solana.
    2. Evaluează lichiditatea, volumul și vechimea.
    3. Calculează un scor orientativ între 0 și 100.
    4. Afișează un clasament și permite exportul CSV.
    """)
    st.warning("Scorul este bazat pe reguli simple, nu este o predicție și nu garantează profit. Verifică separat contractul, distribuția deținătorilor și riscul de rug pull.")
