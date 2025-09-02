import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
import requests

TEMP_DIR = "mi_carpeta/temp_imgs"

def generar_informe_pdf(df_filtrado, filtros=None):
    # --- Preparar carpeta temporal ---
    os.makedirs(TEMP_DIR, exist_ok=True)

    # --- Limpiar nombres de columnas ---
    df_filtrado = df_filtrado.copy()
    df_filtrado.columns = df_filtrado.columns.str.strip()  # eliminar espacios
    df_filtrado.columns = df_filtrado.columns.str.replace('\ufeff', '', regex=True)  # eliminar BOM
    df_filtrado.columns = df_filtrado.columns.str.title()  # estandarizar mayúscula inicial

    # --- Asegurar columna Año numérica ---
    if "Año" in df_filtrado.columns:
        df_filtrado["Año"] = pd.to_numeric(df_filtrado["Año"], errors="coerce")
    else:
        df_filtrado["Año"] = pd.NA

    # --- Eliminar duplicados ---
    df_filtrado = df_filtrado.drop_duplicates(subset=["Titulo", "Director", "Año"], keep="first")

    # --- Crear documento PDF ---
    filename = "Informe_Peliculas.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    # --- Estilos ---
    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Heading2"]
    estilo_texto = styles["Normal"]
    estilo_numeros = ParagraphStyle(
        "Numeros", parent=styles["Normal"], fontSize=12, leading=16, spaceAfter=8, alignment=TA_LEFT
    )

    # --- Título del informe ---
    story.append(Paragraph("📊 Informe de Películas - Top Filtradas", estilo_titulo))
    story.append(Spacer(1, 20))

    # --- Filtros aplicados ---
    if filtros:
        story.append(Paragraph("Filtros aplicados:", estilo_subtitulo))
        for clave, val in filtros.items():
            story.append(Paragraph(f"<b>{clave}:</b> {val if val else 'Todos'}", estilo_texto))
            story.append(Spacer(1, 5))
        story.append(Spacer(1, 15))

    # --- Detalle de películas ---
    for idx, row in df_filtrado.iterrows():
        story.append(Paragraph(f"🎬 {row.get('Titulo', 'Sin título')}", estilo_subtitulo))
        story.append(Paragraph(f"Director: {row.get('Director', 'N/A')} | Año: {row.get('Año', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Género: {row.get('Genero', 'N/A')} | Estrellas: {row.get('Estrellas', 'N/A')}", estilo_texto))
        story.append(Spacer(1, 8))

        # --- Presupuesto, ingresos, ROI ---
        budget = row.get("Budget", 0) or 0
        revenue = row.get("Revenue", 0) or 0
        roi = (revenue - budget) / budget if budget > 0 else None

        texto_numeros = (
            f"<b>Presupuesto:</b> ${budget:,.0f}<br/><b>Ingresos:</b> ${revenue:,.0f}<br/><b>ROI:</b> {roi*100:.2f}%"
            if roi is not None else "❌ ROI no disponible"
        )
        story.append(Paragraph(texto_numeros, estilo_numeros))
        story.append(Spacer(1, 5))

        # --- Poster ---
        poster_url = row.get("Poster-Url")
        if pd.notna(poster_url):
            try:
                img = BytesIO(requests.get(poster_url, timeout=5).content)
                story.append(Image(img, width=200, height=300))
                story.append(Spacer(1, 5))
            except:
                pass

        # --- Gráfico Presupuesto vs Ingresos ---
        plt.figure(figsize=(4, 3))
        if roi is not None:
            plt.bar(["Presupuesto", "Ingresos", "ROI (%)"], [budget, revenue, roi*100])
        else:
            plt.bar(["Presupuesto", "Ingresos"], [budget, revenue])
        plt.title("Presupuesto vs Ingresos y ROI (%)")
        temp_path = os.path.join(TEMP_DIR, f"plot_{idx}.png")
        plt.savefig(temp_path)
        plt.close()
        story.append(Image(temp_path, width=250, height=180))
        story.append(Spacer(1, 10))

        # --- Sinopsis ---
        story.append(Paragraph(f"📖 Sinopsis: {row.get('Overview', 'No disponible')}", estilo_texto))
        story.append(PageBreak())

    # --- Tabla de resumen ---
    if not df_filtrado.empty:
        data = [["Título", "Director", "Año", "Género", "Score"]]
        for _, row in df_filtrado.iterrows():
            data.append([
                row.get("Titulo", ""),
                row.get("Director", ""),
                row.get("Año", ""),
                row.get("Genero", ""),
                row.get("Score", ""),
            ])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No se encontraron películas con los filtros aplicados.", styles["Normal"]))

    # --- Construir PDF ---
    doc.build(story)

    # --- Limpiar carpeta temporal ---
    shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    return filename

# -------------------------------
# USO SUGERIDO:

# filtros = {
#     "Director": ", ".join(director_sel),
#     "Género": ", ".join(genero_sel),
#     "Estrellas": ", ".join(estrellas_sel),
#     "Palabra clave": palabra,
#     "Año entre": f"{año_desde} - {año_hasta}"
# }
# filename = generar_informe_pdf(df_filtrado, filtros)
