import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# --- Cargar datos desde el Excel fijo ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datosBI.xlsx")

    # --- Normalización de columnas problemáticas ---
    if "Año" in df.columns:
        df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
        df = df.dropna(subset=["Año"])
        df["Año"] = df["Año"].astype(int)

    if "budget" in df.columns:
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

    if "revenue" in df.columns:
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

    if "genero" in df.columns:
        # limpiar géneros con llaves u otros símbolos raros
        df["genero"] = (
            df["genero"]
            .astype(str)
            .str.replace(r"[{}]", "", regex=True)
            .str.strip()
        )

    return df


# --- App principal ---
st.set_page_config(page_title="🎬 Análisis de Películas", layout="wide")

st.title("🎬 Explorador de Películas con datos de Excel")
st.markdown("Este explorador trabaja con el archivo **datosBI.xlsx** 📂")

# Cargar DataFrame
df = cargar_datos()

# --- Filtros ---
st.sidebar.header("🔎 Filtros disponibles")

# Filtro de director (case-insensitive + limpieza de duplicados)
if "director" in df.columns:
    directores_unicos = (
        df["director"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.lower()
        .unique()
        .tolist()
    )
    directores_unicos = sorted(set(directores_unicos))
    director_sel = st.sidebar.multiselect("🎬 Elige directores", directores_unicos)
else:
    director_sel = []

# Filtro de estrellas
if "estrellas" in df.columns:
    estrellas_unicas = (
        df["estrellas"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )
    estrellas_unicas = sorted(set(estrellas_unicas))
    estrellas_sel = st.sidebar.multiselect("⭐ Elige estrellas", estrellas_unicas)
else:
    estrellas_sel = []

# Buscar palabra en sinopsis
palabra = st.sidebar.text_input("📖 Buscar palabra clave en sinopsis")

# Rango de años
if "Año" in df.columns:
    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
else:
    año_min, año_max = 1900, 2100

año_desde = st.sidebar.number_input("Año desde", min_value=1900, max_value=2100, value=año_min)
año_hasta = st.sidebar.number_input("Año hasta", min_value=1900, max_value=2100, value=año_max)

# --- Aplicar filtros ---
df_filtrado = df.copy()

if director_sel:
    df_filtrado = df_filtrado[
        df_filtrado["director"].str.lower().isin(director_sel)
    ]

if estrellas_sel:
    df_filtrado = df_filtrado[
        df_filtrado["estrellas"].isin(estrellas_sel)
    ]

if palabra:
    df_filtrado = df_filtrado[
        df_filtrado["overview"].str.contains(palabra, case=False, na=False)
    ]

if "Año" in df.columns:
    df_filtrado = df_filtrado[
        (df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)
    ]

# --- Mostrar resultados ---
st.subheader("📊 Resultados filtrados")
st.write(f"Películas encontradas: {len(df_filtrado)}")
st.dataframe(df_filtrado)

# --- Descargar informe ---
if not df_filtrado.empty:
    if st.button("📥 Descargar Informe en PDF"):
        filename = generar_informe_pdf(df_filtrado)
        with open(filename, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
