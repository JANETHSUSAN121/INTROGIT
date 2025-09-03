import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# --- Configuración de la página ---
st.set_page_config(page_title="Informe de Películas", layout="wide")

st.title("🎬 Películas - Informe PDF")

# --- Cargar datos desde Excel ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datosBI.xlsx")
    df.columns = df.columns.str.strip().str.lower()  # 🔑 normalizar nombres
    
    # Normalizar valores de texto para evitar duplicados raros
    for col in ["director", "genero", "estrellas", "titulo"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
    
    return df

df = cargar_datos()

# --- Opciones de filtrado ---
st.sidebar.header("Filtros")

# Checkbox para eliminar duplicados
eliminar_dupl = st.sidebar.checkbox("Eliminar duplicados por Título + Año", value=True)

# Aplicar eliminación de duplicados si corresponde
if eliminar_dupl and "titulo" in df.columns and "año" in df.columns:
    df = df.drop_duplicates(subset=["titulo", "año"])
elif eliminar_dupl:
    df = df.drop_duplicates()

# Filtros principales
director_sel = st.sidebar.multiselect("Director", options=sorted(df["director"].dropna().unique()))
genero_sel = st.sidebar.multiselect("Género", options=sorted(df["genero"].dropna().unique()))
estrellas_sel = st.sidebar.multiselect("Estrellas", options=sorted(df["estrellas"].dropna().unique()))
año_desde, año_hasta = st.sidebar.slider(
    "Año", 
    int(df["año"].min()), 
    int(df["año"].max()), 
    (int(df["año"].min()), int(df["año"].max()))
)
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
df_filtrado = df_filtrado[(df_filtrado["año"] >= año_desde) & (df_filtrado["año"] <= año_hasta)]

# --- Mostrar DataFrame filtrado ---
st.subheader("Películas disponibles")
st.write(f"Se encontraron **{len(df_filtrado)}** películas con los filtros seleccionados.")
st.dataframe(df_filtrado.reset_index(drop=True))

# --- Botón para generar PDF ---
if st.button("📄 Generar Informe PDF"):
    filtros = {
        "Director": ", ".join(director_sel) if director_sel else "Todos",
        "Género": ", ".join(genero_sel) if genero_sel else "Todos",
        "Estrellas": ", ".join(estrellas_sel) if estrellas_sel else "Todos",
        "Palabra clave": palabra if palabra else "Ninguna",
        "Año entre": f"{año_desde} - {año_hasta}",
        "Eliminar duplicados": "Sí" if eliminar_dupl else "No"
    }
    archivo_pdf = generar_informe_pdf(df_filtrado, filtros)
    with open(archivo_pdf, "rb") as f:
        st.download_button("⬇️ Descargar PDF", f, file_name=archivo_pdf)
