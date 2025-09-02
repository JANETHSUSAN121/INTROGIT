import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

st.set_page_config(page_title="Explorador de Películas", layout="wide")

st.title("🎬 Explorador de Películas")
st.write("Filtra películas y genera informes en PDF.")

# --- Cargar archivo ---
xlsx_path = "datosBI.xlsx"
df = pd.read_excel(xlsx_path)

if archivo is not None:
    try:
        df = pd.read_excel(archivo)

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
            df["genero"] = df["genero"].astype(str).str.replace(r"[{}]", "", regex=True).str.strip()

        # --- Filtros ---
        directores = df["director"].dropna().unique().tolist() if "director" in df.columns else []
        director_sel = st.multiselect("Elige directores", directores)

        palabra = st.text_input("Buscar palabra clave en sinopsis")

        año_min = int(df["Año"].min()) if "Año" in df.columns else 1900
        año_max = int(df["Año"].max()) if "Año" in df.columns else 2100

        año_desde = st.number_input("Año desde", min_value=1900, max_value=2100, value=año_min)
        año_hasta = st.number_input("Año hasta", min_value=1900, max_value=2100, value=año_max)

        # --- Aplicar filtros ---
        df_filtrado = df.copy()

        if director_sel:
            df_filtrado = df_filtrado[df_filtrado["director"].isin(director_sel)]

        if palabra:
            df_filtrado = df_filtrado[df_filtrado["overview"].str.contains(palabra, case=False, na=False)]

        df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)]

        # --- Mostrar resultados ---
        st.write("### 📊 Resultados", df_filtrado)

        if not df_filtrado.empty:
            if st.button("📑 Generar Informe PDF"):
                filename = generar_informe_pdf(df_filtrado)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Descargar Informe PDF", f, file_name=filename)

    except Exception as e:
        st.error(f"❌ Error al cargar o procesar el archivo xlsx: {e}")
    
     
