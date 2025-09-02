import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# --- Función para normalizar columnas ---
def normalizar_columnas(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace('\ufeff','', regex=True).str.lower()
    return df

st.title("🎬 App de Películas")

# --- Cargar Excel directamente ---
df = pd.read_excel("datosBI.xlsx")
df = normalizar_columnas(df)

st.write(f"Datos cargados: {len(df)} filas")

# --- Selección de filtros ---
directores = st.multiselect("Selecciona Director(es):", options=df["director"].dropna().unique())
generos = st.multiselect("Selecciona Género(s):", options=df["genero"].dropna().unique())
estrellas = st.multiselect("Selecciona Estrellas:", options=df["estrellas"].dropna().unique())
palabra = st.text_input("Palabra clave en título o sinopsis:")
año_desde, año_hasta = st.slider(
    "Rango de años:",
    int(df["año"].min()), int(df["año"].max()),
    (int(df["año"].min()), int(df["año"].max()))
)

# --- Filtrar DataFrame ---
df_filtrado = df.copy()
if directores:
    df_filtrado = df_filtrado[df_filtrado["director"].isin(directores)]
if generos:
    df_filtrado = df_filtrado[df_filtrado["genero"].isin(generos)]
if estrellas:
    df_filtrado = df_filtrado[df_filtrado["estrellas"].isin(estrellas)]
if palabra:
    df_filtrado = df_filtrado[
        df_filtrado["titulo"].str.contains(palabra, case=False, na=False) |
        df_filtrado["overview"].str.contains(palabra, case=False, na=False)
    ]

# --- Filtrar rango de años ---
df_filtrado = df_filtrado[
    df_filtrado["año"].notna() &
    (df_filtrado["año"] >= año_desde) &
    (df_filtrado["año"] <= año_hasta)
]

st.write(f"Se encontraron {len(df_filtrado)} películas con los filtros aplicados.")

# --- Generar PDF ---
if st.button("Generar Informe PDF"):
    filtros = {
        "Director": ", ".join(directores) if directores else "Todos",
        "Género": ", ".join(generos) if generos else "Todos",
        "Estrellas": ", ".join(estrellas) if estrellas else "Todos",
        "Palabra clave": palabra if palabra else "Ninguna",
        "Año entre": f"{año_desde} - {año_hasta}"
    }

    archivo_pdf = generar_informe_pdf(df_filtrado, filtros)
    st.success(f"PDF generado: {archivo_pdf}")
    st.download_button("📥 Descargar PDF", archivo_pdf)
 
