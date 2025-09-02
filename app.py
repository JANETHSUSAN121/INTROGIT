import os
import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# 📂 Ruta del Excel
xlsx_path = "datosBI.xlsx"

if not os.path.exists(xlsx_path):
    st.error(f"❌ No se encontró {xlsx_path}. Asegúrate de que el archivo esté en el repo.")
else:
    try:
        # ✅ Leer archivo Excel (.xlsx)
        df = pd.read_excel(xlsx_path)

        # --- Normalizar columnas ---
        df.columns = df.columns.str.strip()  # limpiar espacios en los nombres
        if "genero" in df.columns:
            df["genero"] = df["genero"].astype(str).str.replace(r"[{}]", "", regex=True).str.strip()

        if "Año" in df.columns:
            df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
            df = df.dropna(subset=["Año"])
            df["Año"] = df["Año"].astype(int)

        if "budget" in df.columns:
            df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

        if "revenue" in df.columns:
            df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

        st.title("🎬 Recomendador de Películas")

        # --- Filtros ---
        generos = st.multiselect(
            "Elige géneros",
            df["genero"].dropna().unique().tolist() if "genero" in df.columns else []
        )

        directores = st.multiselect(
            "Elige directores",
            df["Director"].dropna().unique().tolist() if "Director" in df.columns else []
        )

        estrellas = st.multiselect(
            "Elige estrellas",
            df["estrellas"].dropna().unique().tolist() if "estrellas" in df.columns else []
        )

        palabra = st.text_input("Buscar palabra clave en sinopsis")

        año_min = int(df["Año"].min()) if "Año" in df.columns else 1900
        año_max = int(df["Año"].max()) if "Año" in df.columns else 2100
        año_desde = st.number_input("Año desde", min_value=1900, max_value=2100, value=año_min)
        año_hasta = st.number_input("Año hasta", min_value=1900, max_value=2100, value=año_max)

        # --- Aplicar filtros ---
        df_filtrado = df.copy()

        if generos:
            df_filtrado = df_filtrado[df_filtrado["genero"].isin(generos)]
        if directores:
            df_filtrado = df_filtrado[df_filtrado["Director"].isin(directores)]
        if estrellas:
            df_filtrado = df_filtrado[df_filtrado["estrellas"].isin(estrellas)]
        if palabra and "overview" in df.columns:
            df_filtrado = df_filtrado[df_filtrado["overview"].str.contains(palabra, case=False, na=False)]
        if "Año" in df_filtrado.columns:
            df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_desde) & (df_filtrado["Año"] <= año_hasta)]

        # --- Calcular ROI ---
        if "budget" in df_filtrado.columns and "revenue" in df_filtrado.columns:
            df_filtrado["ROI"] = df_filtrado.apply(
                lambda x: (x["revenue"] - x["budget"]) / x["budget"] if pd.notna(x["budget"]) and x["budget"] > 0 else None,
                axis=1
            )
        else:
            df_filtrado["ROI"] = None

        # --- Ranking ---
        if "score" in df_filtrado.columns:
            df_filtrado["ranking"] = df_filtrado.apply(
                lambda x: x["ROI"] if pd.notna(x["ROI"]) else x.get("score", 0),
                axis=1
            )
        else:
            df_filtrado["ranking"] = df_filtrado["ROI"]

        # --- Seleccionar Top 10 ---
        peliculas_top = df_filtrado.sort_values(by="ranking", ascending=False).head(10)

        # --- Mostrar resultados ---
        st.subheader("🎯 Resultado(s) según filtros y ranking")
        if peliculas_top.empty:
            st.warning("⚠️ No se encontraron películas con esos filtros")
        else:
            cols_to_show = [
                c for c in ["titulo", "Año", "genero", "Director", "estrellas", "score", "budget", "revenue", "ROI"]
                if c in peliculas_top.columns
            ]
            st.dataframe(peliculas_top[cols_to_show])

            # --- Botón PDF ---
            if st.button("📄 Generar informe PDF"):
                filename = generar_informe_pdf(peliculas_top)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Descargar Informe", f, file_name="Informe_Peliculas.pdf")

    except Exception as e:
        st.error(f"❌ Error al cargar o procesar el archivo xlsx : {e}")
    
        
       
