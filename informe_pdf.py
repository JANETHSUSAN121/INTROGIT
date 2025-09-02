import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
import os
import shutil

TEMP_DIR = "mi_carpeta/temp_imgs"
os.makedirs(TEMP_DIR, exist_ok=True)

def generar_informe_pdf(df_filtrado, filtros):
    # Eliminar duplicados
    df_filtrado = df_filtrado.drop_duplicates(subset=["titulo", "Director", "Año"], keep="first")
    
    filename = "Informe_Peliculas.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Heading2"]
    estilo_texto = styles["Normal"]
    estilo_numeros = ParagraphStyle(
        "Numeros", parent=styles["Normal"], fontSize=12, leading=16, spaceAfter=8, alignment=TA_LEFT
    )

    # 1) Título del informe
    story.append(Paragraph("📊 Informe de Películas - Top Filtradas", estilo_titulo))
    story.append(Spacer(1, 20))

    # 2) Resumen de filtros aplicados
    story.append(Paragraph("Filtros aplicados:", estilo_subtitulo))
    for clave, val in filtros.items():
        story.append(Paragraph(f"<b>{clave}:</b> {val if val else 'Todos'}", estilo_texto))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 15))

    # 3) Detalle de películas
    for idx, row in df_filtrado.iterrows():
        story.append(Paragraph(f"🎬 {row.get('titulo', 'Sin título')}", estilo_subtitulo))
        story.append(Paragraph(f"Director: {row.get('Director', 'N/A')} | Año: {row.get('Año', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Género: {row.get('genero', 'N/A')} | Estrellas: {row.get('estrellas', 'N/A')}", estilo_texto))
        story.append(Spacer(1, 8))

        budget = row.get("budget", 0) or 0
        revenue = row.get("revenue", 0) or 0
        budget = budget if pd.notna(budget) else 0
        revenue = revenue if pd.notna(revenue) else 0
        roi = (revenue - budget) / budget if budget and budget > 0 else None

        texto_numeros = (
            f"<b>Presupuesto:</b> ${budget:,.0f}<br/><b>Ingresos:</b> ${revenue:,.0f}<br/><b>ROI:</b> {roi*100:.2f}%"
            if roi is not None else "❌ ROI no disponible"
        )
        story.append(Paragraph(texto_numeros, estilo_numeros))
        story.append(Spacer(1, 5))

        if pd.notna(row.get("poster-url")):
            try:
                from io import BytesIO
                import requests
                img = BytesIO(requests.get(row["poster-url"], timeout=5).content)
                story.append(Image(img, width=200, height=300))
                story.append(Spacer(1, 5))
            except:
                pass

        plt.figure(figsize=(4, 3))
        if roi is not None:
            plt.bar(["Presupuesto", "Ingresos", "ROI (%)"], [budget, revenue, roi * 100])
        else:
            plt.bar(["Presupuesto", "Ingresos"], [budget, revenue])
        plt.title("Presupuesto vs Ingresos y ROI (%)")
        temp_path = os.path.join(TEMP_DIR, f"plot_{idx}.png")
        plt.savefig(temp_path)
        plt.close()
        story.append(Image(temp_path, width=250, height=180))

        story.append(Spacer(1, 10))
        story.append(Paragraph(f"📖 Sinopsis: {row.get('overview', 'No disponible')}", estilo_texto))
        story.append(PageBreak())

    doc.build(story)

    # Limpiar carpeta temporal
    shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    return filename
Uso sugerido (en app.py al llamar a generar_informe_pdf):
python
Copiar código
filtros = {
    "Director": ", ".join(director_sel),
    "Género": ", ".join(genero_sel),
    "Estrellas": ", ".join(estrellas_sel),
    "Palabra clave": palabra,
    "Año entre": f"{año_desde} - {año_hasta}"
}
filename = generar_informe_pdf(df_filtrado, filtros)
