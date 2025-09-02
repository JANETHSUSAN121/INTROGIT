import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf
# --- Cargar datos ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("datosBI.xlsx")
 # Normalización básica de columnas
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

    if "Director" in df.columns:
        df["Director"] = df["Director"].astype(str).str.strip()

    if "estrellas" in df.columns:
        df["estrellas"] = df["estrellas"].astype(str).str.strip()

    return df


# --- Interfaz principal ---
st.title("🎬 Análisis de Películas")

df = cargar_datos()

# --- Filtros ---
directores = sorted(df["Director"].dropna().unique().tolist()) if "Director" in df.columns else []
generos = sorted(df["genero"].dropna().unique().tolist()) if "genero" in df.columns else []
estrellas = sorted(df["estrellas"].dropna().unique().tolist()) if "estrellas" in df.columns else []

director_sel = st.multiselect("🎥 Elige directores", directores)
genero_sel = st.multiselect("📚 Elige géneros", generos)
estrella_sel = st.multiselect("⭐ Elige estrellas", estrellas)

palabra = st.text_input("🔍 Buscar palabra clave en sinopsis")

año_min = int(df["Año"].min()) if "Año" in df.columns else 1900
año_max = int(df["Año"].max()) if "Año" in df.columns else 2100
año_desde = st.number_input("Año desde", min_value=1900, max_value=2100, value=año_min)
año_hasta = st.number_input("Año hasta", min_value=1900, max_value=2100, value=año_max)

# --- Aplicar filtros ---
df_filtrado = df.copy()

if director_sel:
    df_filtrado = df_filtrado[
        df_filtrado["Director"].str.lower().str.contains("|".join([d.lower() for d in director_sel]))
    ]

if genero_sel:
    df_filtrado = df_filtrado[
        df_filtrado["genero"].str.lower().str.contains("|".join([g.lower() for g in genero_sel]))
    ]

if estrella_sel:
    df_filtrado = df_filtrado[
        df_filtrado["estrellas"].str.lower().str.contains("|".join([e.lower() for e in estrella_sel]))
    ]

if palabra:
    df_filtrado = df_filtrado[
        df_filtrado["overview"].str.lower().str.contains(palabra.lower(), na=False)
    ]

df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)]

# --- Eliminar duplicados ---
df_filtrado = df_filtrado.drop_duplicates(subset=["titulo", "Director", "Año"], keep="first")

# --- Botón para mostrar resultados ---
if st.button("👀 Ver películas filtradas"):
    if not df_filtrado.empty:
        st.write("### Resultados filtrados")
        st.dataframe(df_filtrado[["titulo", "Director", "Año", "genero", "score"]])
    else:
        st.warning("⚠️ No se encontraron películas con esos filtros.")

# --- Botón para generar informe ---
if st.button("📄 Generar informe PDF"):
    if not df_filtrado.empty:
        filename = generar_informe_pdf(df_filtrado)
        with open(filename, "rb") as f:
            st.download_button("⬇️ Descargar Informe", f, file_name=filename)
    else:
        st.warning("⚠️ No hay datos filtrados para generar el informe.")
