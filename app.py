import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# ================================
# 📂 Cargar datos desde Excel
# ================================
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datosBI.xlsx")

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
        df["genero"] = (
            df["genero"]
            .astype(str)
            .str.replace(r"[{}]", "", regex=True)
            .str.strip()
        )

    return df


df = cargar_datos()

# ================================
# 🎛️ Barra lateral de filtros
# ================================
st.sidebar.header("🎬 Filtros")

# Filtro de director
if "Director" in df.columns:
    directores_unicos = (
        df["Director"].dropna().astype(str).str.strip().unique().tolist()
    )
    opciones_directores = sorted(set(directores_unicos))
    director_sel = st.sidebar.multiselect("🎬 Elige directores", opciones_directores)
else:
    director_sel = []

# Filtro de género
if "genero" in df.columns:
    generos_unicos = (
        df["genero"].dropna().astype(str).str.strip().unique().tolist()
    )
    opciones_generos = sorted(set(generos_unicos))
    genero_sel = st.sidebar.multiselect("🎭 Elige géneros", opciones_generos)
else:
    genero_sel = []

# Filtro de estrellas
if "estrellas" in df.columns:
    estrellas_unicos = (
        df["estrellas"].dropna().astype(str).str.strip().unique().tolist()
    )
    opciones_estrellas = sorted(set(estrellas_unicos))
    estrellas_sel = st.sidebar.multiselect("⭐ Elige estrellas", opciones_estrellas)
else:
    estrellas_sel = []

# Filtro de palabra clave en sinopsis
palabra = st.sidebar.text_input("🔎 Buscar palabra clave en sinopsis")

# Filtro de rango de años
if "Año" in df.columns:
    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
else:
    año_min, año_max = 1900, 2100

año_desde = st.sidebar.number_input(
    "📅 Año desde", min_value=1900, max_value=2100, value=año_min
)
año_hasta = st.sidebar.number_input(
    "📅 Año hasta", min_value=1900, max_value=2100, value=año_max
)

# ================================
# 📊 Aplicar filtros
# ================================
df_filtrado = df.copy()

# Filtro de director (case-insensitive)
if director_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Director"].str.lower().isin([d.lower() for d in director_sel])
    ]

# Filtro de género
if genero_sel:
    df_filtrado = df_filtrado[
        df_filtrado["genero"].str.lower().isin([g.lower() for g in genero_sel])
    ]

# Filtro de estrellas (case-insensitive)
if estrellas_sel:
    df_filtrado = df_filtrado[
        df_filtrado["estrellas"].str.lower().isin([e.lower() for e in estrellas_sel])
    ]

# Filtro de palabra clave
if palabra:
    df_filtrado = df_filtrado[
        df_filtrado["overview"].str.contains(palabra, case=False, na=False)
    ]

# Filtro de años
if "Año" in df.columns:
    df_filtrado = df_filtrado[
        (df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)
    ]

# ================================
# 📋 Mostrar resultados
# ================================
st.write("### 🎥 Películas filtradas")
st.dataframe(df_filtrado)

# ================================
# 📑 Botón para generar informe PDF
# ================================
if st.button("📥 Descargar informe PDF"):
    if not df_filtrado.empty:
        nombre_pdf = generar_informe_pdf(df_filtrado)
        with open(nombre_pdf, "rb") as f:
            st.download_button(
                "📄 Descargar informe",
                f,
                file_name=nombre_pdf,
                mime="application/pdf",
            )
    else:
        st.warning("⚠️ No hay datos filtrados para generar el informe.")
