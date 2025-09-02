import os
import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# 📂 Ruta del Excel en tu repo
xlsx_path = "datosBI.xlsx"

if not os.path.exists(xlsx_path):
    st.error(f"❌ No se encontró {xlsx_path}. Asegúrate de subirlo al repo.")
else:
    try:
        # ✅ Leer archivo Excel
        df = pd.read_excel(xlsx_path)

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

        # --- Filtros ---
        st.title("🎬 Recomendador de Películas")

        generos = st.multiselect(
            "Elige géneros",
            df["genero"].dropna().unique().tolist() if "genero" in df.columns else [],
        )
        directores = st.multiselect(
            "Elige directores",
            df["director"].dropna().unique().tolist() if "director" in df.columns else [],
        )
        palabra = st.text_input("Buscar palabra clave en sinopsis")

        año_min = int(df["Año"].min()) if "Año" in df.columns else 1900
        año_max = int(df["Año"].max()) if "Año" in df.columns else 2100

        año_desde = st.number_input(
            "Año desde", min_value=1900, max_value=2100, value=año_min
        )
        año_hasta = st.number_input(
            "Año hasta", min_value=1900, max_value=2100, value=año_max
        )

        # --- Aplicar filtros ---
        df_filtrado = df.copy()

        # Aquí puedes seguir con tu lógica de filtrado y generación de informe
        # Ejemplo: generar el PDF
        if st.button("📄 Generar Informe PDF"):
            archivo_pdf = generar_informe_pdf(df_filtrado)
            with open(archivo_pdf, "rb") as f:
                st.download_button(
                    "⬇️ Descargar Informe",
                    f,
                    file_name=archivo_pdf,
                    mime="application/pdf",
                )

    except Exception as e:
        st.error(f"❌ Error al cargar o procesar el archivo xlsx: {e}")
