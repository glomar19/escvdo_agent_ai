import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).parent
sys.path.append(str(ROOT / "src"))
from report import top_insights, GARMENTS, ES

NAMES = {"escvdo": "ESCVDO", "chloe": "Chloé"}

st.set_page_config(page_title="ESCVDO Competitor Trend Agent", layout="wide")
st.title("ESCVDO Competitor Trend Agent")
st.caption("Compara ESCVDO con un competidor: prendas, colores y patrones.")

df = pd.read_csv(ROOT / "data/final_table.csv")
competitors = [b for b in sorted(df["brand"].unique()) if b != "escvdo"]
comp = st.selectbox("Competidor", competitors, format_func=lambda b: NAMES.get(b, b))
comp_name = NAMES.get(comp, comp)

own_df, comp_df = df[df["brand"] == "escvdo"], df[df["brand"] == comp]

st.header("5 insights para la buyer")
for t in top_insights(df, "escvdo", comp, "ESCVDO", comp_name):
    st.write("• " + t)

def garment_share(d):
    return pd.Series({ES[g]: d["labels_manual"].str.split("|").apply(lambda x: g in x).mean()
                      for g in GARMENTS})

st.header("Prendas (% de fotos que las contienen)")
st.bar_chart(pd.DataFrame({"ESCVDO": garment_share(own_df), comp_name: garment_share(comp_df)}))

def share(col):
    t = pd.DataFrame({"ESCVDO": own_df[col].value_counts(normalize=True),
                      comp_name: comp_df[col].value_counts(normalize=True)}).fillna(0)
    t.index = [ES.get(i, i) for i in t.index]
    return t

st.header("Colores de la parte de arriba")
st.bar_chart(share("color_upper"))

st.header("Patrones")
st.bar_chart(share("pattern_final"))

with st.expander("Limitaciones"):
    st.write(
        "- Las prendas se etiquetaron a mano (ESCVDO: 52 fotos, Chloé: 53).\n"
        "- El color y el patrón son automáticos: color acertó unas 5 de 8 fotos revisadas, "
        "patrón 6 de 8. Los colores claros y la piel oscura fallan.\n"
        "- ESCVDO son fotos de catálogo y Chloé de pasarela, así que la comparación es aproximada."
    )