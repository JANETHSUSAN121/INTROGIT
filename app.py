import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

st.set_page_config(page_title="Informe de Películas", layout="wide")

st.title("🎬 Películas - Informe PDF")

# --- Cargar datos desde Excel ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datosBI.xlsx")
    return df

df = cargar_datos()

# --- Opciones de filtrado ---
st.sidebar.header("Filtros")
director_sel = st.sidebar.multiselect("Director", options=df["Director"].dropna().unique())
genero_sel = st.sidebar.multiselect("Género", options=df["genero"].dropna().unique())
estrellas_sel = st.sidebar.multiselect("Estrellas", options=df["estrellas"].dropna().unique())
año_desde, año_hasta = st.sidebar.slider("Año", int(df["Año"].min()), int(df["Año"].max()), (int(df["Año"].min()), int(df["Año"].max())))
palabra = st.sidebar.text_input("Palabra clave en título")

# --- Filtrar datos ---
df_filtrado = df.copy()
if director_sel:
    df_filtrado = df_filtrado[df_filtrado["director"].isin(director_sel)]
if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["genero"].isin(genero_sel)]
if estrellas_sel:
    df_filtrado = df_filtrado[df_filtrado["estrellas"].isin(estrellas_sel)]
if palabra:
    df_filtrado = df_filtrado[df_filtrado["titulo"].str.contains(palabra, case=False, na=False)]
df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)]

# --- Mostrar DataFrame filtrado ---
st.subheader("Películas disponibles")
st.dataframe(df_filtrado.reset_index(drop=True))

# --- Botón para generar PDF ---
if st.button("📄 Generar Informe PDF"):
    filtros = {
        "Director": ", ".join(director_sel) if director_sel else "Todos",
        "Género": ", ".join(genero_sel) if genero_sel else "Todos",
        "Estrellas": ", ".join(estrellas_sel) if estrellas_sel else "Todos",
        "Palabra clave": palabra if palabra else "Ninguna",
        "Año entre": f"{año_desde} - {año_hasta}"
    }
    archivo_pdf = generar_informe_pdf(df_filtrado, filtros)
    with open(archivo_pdf, "rb") as f:
        st.download_button("⬇️ Descargar PDF", f, file_name=archivo_pdf)
 
    
