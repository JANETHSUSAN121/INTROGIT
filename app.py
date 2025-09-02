import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# --- Cargar datos desde tu Excel ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("peliculas.xlsx")

    # --- Normalización de columnas ---
    if "Año" in df.columns:
        df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
        df = df.dropna(subset=["Año"])
        df["Año"] = df["Año"].astype(int)

    if "budget" in df.columns:
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

    if "genero" in df.columns:
        df["genero"] = df["genero"].astype(str).str.replace(r"[{}]", "", regex=True).str.strip()

    return df


# --- App principal ---
st.set_page_config(page_title="🎬 Informe de Películas", layout="wide")
st.title("🎥 Informe interactivo de películas")

# Cargar datos
df = cargar_datos()
df_filtrado = df.copy()

# ==========================
# 🔎 Filtros
# ==========================

# --- Directores ---
if "Director" in df.columns:
    directores = sorted(df["Director"].dropna().unique().tolist())
    busqueda_director = st.text_input("🔎 Buscar director", "")
    if busqueda_director:
        candidatos = [d for d in directores if busqueda_director.lower() in d.lower()]
    else:
        candidatos = directores
    director_sel = st.multiselect("🎬 Elige directores", candidatos)
    if director_sel:
        df_filtrado = df_filtrado[
            df_filtrado["Director"].str.lower().isin([d.lower() for d in director_sel])
        ]

# --- Estrellas ---
if "estrellas" in df.columns:
    estrellas = sorted(df["estrellas"].dropna().unique().tolist())
    busqueda_estrella = st.text_input("🔎 Buscar estrella", "")
    if busqueda_estrella:
        candidatos_e = [e for e in estrellas if busqueda_estrella.lower() in e.lower()]
    else:
        candidatos_e = estrellas
    estrella_sel = st.multiselect("⭐ Elige estrellas", candidatos_e)
    if estrella_sel:
        df_filtrado = df_filtrado[
            df_filtrado["estrellas"].str.lower().isin([e.lower() for e in estrella_sel])
        ]

# --- Género ---
if "genero" in df.columns:
    generos = sorted(df["genero"].dropna().unique().tolist())
    genero_sel = st.multiselect("🎭 Elige géneros", generos)
    if genero_sel:
        df_filtrado = df_filtrado[
            df_filtrado["genero"].str.lower().isin([g.lower() for g in genero_sel])
        ]

# --- Palabra clave en sinopsis ---
palabra = st.text_input("📖 Buscar palabra clave en sinopsis")
if palabra and "overview" in df.columns:
    df_filtrado = df_filtrado[df_filtrado["overview"].str.contains(palabra, case=False, na=False)]

# --- Años ---
if "Año" in df.columns:
    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
    año_desde, año_hasta = st.slider("📅 Rango de años", año_min, año_max, (año_min, año_max))
    df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)]

# ==========================
# 📊 Resultados
# ==========================
st.subheader("🎬 Resultados filtrados")
st.write(f"Películas encontradas: {len(df_filtrado)}")
st.dataframe(df_filtrado)

# ==========================
# 📥 Generar informe PDF
# ==========================
if not df_filtrado.empty:
    if st.button("📄 Generar informe PDF"):
        pdf_file = generar_informe_pdf(df_filtrado)
        with open(pdf_file, "rb") as f:
            st.download_button("⬇️ Descargar Informe PDF", f, file_name=pdf_file, mime="application/pdf")
