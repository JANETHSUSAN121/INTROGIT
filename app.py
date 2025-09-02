import os
import streamlit as st
import pandas as pd
from informe_pdf import generar_informe_pdf

# 📂 Ruta del Excel
xlsx_path = "datosBI.xlsx"

if not os.path.exists(xlsx_path):
    st.error(f"❌ No se encontró {xlsx_path}. Asegúrate de subirlo al repo.")
else:
    try:
        # ✅ Leer archivo Excel (.xlsx)
        df = pd.read_excel(xlsx_path)

        # 🔹 Forzar columnas numéricas si existen
        numeric_cols = ["budget", "revenue", "score", "Año"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 🔹 Limpiar columna genero
        if "genero" in df.columns:
            df["genero"] = (
                df["genero"]
                .astype(str)
                .str.strip()
                .str.replace(r"[{}]", "", regex=True)  # quitar llaves o símbolos
                .str.replace(r"\s+", " ", regex=True)  # quitar espacios dobles
            )

        st.title("🎬 Recomendador de Películas")

        # 🔹 Filtros
        generos = st.multiselect(
            "Elige géneros",
            options=df["genero"].dropna().unique() if "genero" in df.columns else []
        )
        directores = st.multiselect(
            "Elige directores",
            options=df["director"].dropna().unique() if "director" in df.columns else []
        )
        palabra = st.text_input("Buscar palabra clave en sinopsis")
        fecha_ini = st.number_input("Año desde", min_value=1900, max_value=2100, value=1900)
        fecha_fin = st.number_input("Año hasta", min_value=1900, max_value=2100, value=2100)

        # 🔹 Aplicar filtros
        peliculas = df.copy()
        if generos and "genero" in peliculas.columns:
            peliculas = peliculas[peliculas["genero"].isin(generos)]
        if directores and "director" in peliculas.columns:
            peliculas = peliculas[peliculas["director"].isin(directores)]
        if palabra and "overview" in peliculas.columns:
            peliculas = peliculas[peliculas["overview"].str.contains(palabra, case=False, na=False)]
        if "Año" in peliculas.columns:
            peliculas = peliculas[
                (peliculas["Año"].notna()) &
                (peliculas["Año"] >= fecha_ini) &
                (peliculas["Año"] <= fecha_fin)
            ]

        # 🔹 Filtro por película específica (opcional)
        if not peliculas.empty and "titulo" in peliculas.columns:
            peli_opt = ["(Todas)"] + sorted(peliculas["titulo"].dropna().unique().tolist())
            pelicula_seleccionada = st.selectbox("Elige una película específica (opcional)", options=peli_opt)
            if pelicula_seleccionada != "(Todas)":
                peliculas = peliculas[peliculas["titulo"] == pelicula_seleccionada]

        # 🔹 Calcular ROI
        if "budget" in peliculas.columns and "revenue" in peliculas.columns:
            peliculas["ROI"] = peliculas.apply(
                lambda x: (x["revenue"] - x["budget"]) / x["budget"] if pd.notna(x["budget"]) and x["budget"] > 0 else None,
                axis=1
            )
        else:
            peliculas["ROI"] = None

        # 🔹 Ranking: ROI si existe, si no usar score
        if "score" in peliculas.columns:
            peliculas["ranking"] = peliculas.apply(
                lambda x: x["ROI"] if pd.notna(x["ROI"]) else x.get("score", 0),
                axis=1
            )
        else:
            peliculas["ranking"] = peliculas["ROI"]

        # ✅ Forzar ranking a numérico
        peliculas["ranking"] = pd.to_numeric(peliculas["ranking"], errors="coerce")

        # 🔹 Seleccionar Top 10
        peliculas_top = peliculas.sort_values(by="ranking", ascending=False).head(10)

        # 🔹 Mostrar resultados
        st.subheader("🎯 Resultado(s) según filtros y ranking")
        if peliculas_top.empty:
            st.warning("⚠️ No se encontraron películas con esos filtros")
        else:
            cols_to_show = [c for c in ["titulo", "Año", "genero", "director", "score", "budget", "revenue", "ROI"] if c in peliculas_top.columns]
            st.dataframe(peliculas_top[cols_to_show])

            # 🔹 Botón PDF
            if st.button("📄 Generar informe PDF"):
                filename = generar_informe_pdf(peliculas_top)
                with open(filename, "rb") as f:
                    st.download_button("⬇️ Descargar Informe", f, file_name="Informe_Peliculas.pdf")

    except Exception as e:
        st.error(f"❌ Error al cargar o procesar el archivo xlsx : {e}")
    
     
