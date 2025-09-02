import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
import requests

def generar_informe_pdf(df_filtrado, filtros=None):
    # --- Limpiar nombres de columna ---
    df_filtrado = df_filtrado.copy()
    df_filtrado.columns = df_filtrado.columns.str.strip().str.replace('\ufeff','', regex=True).str.lower()

    # --- Asegurar columna 'año' numérica ---
    if "año" not in df_filtrado.columns:
        df_filtrado["año"] = pd.NA
    df_filtrado["año"] = pd.to_numeric(df_filtrado["año"], errors="coerce")

    # --- Eliminar duplicados ---
    df_filtrado = df_filtrado.drop_duplicates(subset=["titulo", "director", "año"], keep="first")

    # --- Crear PDF ---
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

    # --- Título ---
    story.append(Paragraph("📊 Informe de Películas - Top Filtradas", estilo_titulo))
    story.append(Spacer(1, 20))

    # --- Filtros ---
    if filtros:
        story.append(Paragraph("Filtros aplicados:", estilo_subtitulo))
        for clave, val in filtros.items():
            story.append(Paragraph(f"<b>{clave}:</b> {val if val else 'Todos'}", estilo_texto))
            story.append(Spacer(1, 5))
        story.append(Spacer(1, 15))

    # --- Detalle de películas ---
    for idx, row in df_filtrado.iterrows():
        story.append(Paragraph(f"🎬 {row.get('titulo', 'Sin título')}", estilo_subtitulo))
        story.append(Paragraph(f"Director: {row.get('director', 'N/A')} | Año: {row.get('año', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Género: {row.get('genero', 'N/A')} | Estrellas: {row.get('estrellas', 'N/A')}", estilo_texto))
        story.append(Spacer(1, 8))

        budget = row.get("budget", 0) or 0
        revenue = row.get("revenue", 0) or 0
        roi = (revenue - budget) / budget if budget > 0 else None

        texto_numeros = (
            f"<b>Presupuesto:</b> ${budget:,.0f}<br/><b>Ingresos:</b> ${revenue:,.0f}<br/><b>ROI:</b> {roi*100:.2f}%"
            if roi is not None else "❌ ROI no disponible"
        )
        story.append(Paragraph(texto_numeros, estilo_numeros))
        story.append(Spacer(1, 5))

        # --- Poster ---
        poster_url = row.get("poster-url")
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
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=250, height=180))
        story.append(Spacer(1, 10))

        # --- Sinopsis ---
        story.append(Paragraph(f"📖 Sinopsis: {row.get('overview', 'No disponible')}", estilo_texto))
        story.append(PageBreak())

    # --- Tabla resumen ---
    if not df_filtrado.empty:
        data = [["Título", "Director", "Año", "Género", "Score"]]
        for _, row in df_filtrado.iterrows():
            data.append([
                row.get("titulo", ""),
                row.get("director", ""),
                row.get("año", ""),
                row.get("genero", ""),
                row.get("score", ""),
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

    doc.build(story)
    return filename
