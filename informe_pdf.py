
 import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
import requests
from io import BytesIO
import os
import shutil

# Crear carpeta temporal para imágenes
TEMP_DIR = "mi_carpeta/temp_imgs"
os.makedirs(TEMP_DIR, exist_ok=True)

def generar_informe_pdf(df_filtrado):
    top10 = df_filtrado.head(10)
    filename = "Informe_Peliculas.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Heading1"]
    estilo_texto = styles["Normal"]
    estilo_numeros = ParagraphStyle(
        "Numeros",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        spaceAfter=8,
        alignment=TA_LEFT,
    )

    story.append(Paragraph("📊 Informe de Películas - Top 10", estilo_titulo))
    story.append(Spacer(1, 20))

    for idx, row in top10.iterrows():
        story.append(Paragraph(f"🎬 {row.get('titulo', 'Sin título')}", estilo_subtitulo))
        story.append(Paragraph(f"Director: {row.get('director', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Año: {row.get('Año', 'N/A')} | Score: {row.get('score', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Género: {row.get('genero', 'N/A')}", estilo_texto))
        story.append(Paragraph(f"Duración: {row.get('runtime', 'N/A')} min", estilo_texto))
        story.append(Paragraph(f"Actores principales: {row.get('estrellas', 'No disponible')}", estilo_texto))
        story.append(Spacer(1, 10))

        # --- Presupuesto, Ingresos y ROI
        budget = row.get("budget", 0)
        revenue = row.get("revenue", 0)
        budget = budget if pd.notna(budget) else 0
        revenue = revenue if pd.notna(revenue) else 0
        roi = (revenue - budget) / budget if budget and budget > 0 else None

        if roi is not None:
            texto_numeros = f"""
            <b>Presupuesto:</b> ${budget:,.0f}<br/>
            <b>Ingresos:</b> ${revenue:,.0f}<br/>
            <b>ROI:</b> {roi*100:.2f}%"""
        else:
            texto_numeros = "❌ ROI no disponible por falta de datos"
        story.append(Paragraph(texto_numeros, estilo_numeros))
        story.append(Spacer(1, 10))

        # --- Poster
        poster_url = row.get("poster-url")
        if pd.notna(poster_url):
            try:
                response = requests.get(poster_url, timeout=5)
                if response.status_code == 200:
                    img = BytesIO(response.content)
                    story.append(Image(img, width=200, height=300))
            except:
                pass

        # --- Gráfico Presupuesto vs Ingresos y ROI ---
        plt.figure(figsize=(4, 3))
        if roi is not None:
            plt.bar(["Presupuesto", "Ingresos", "ROI (%)"], [budget, revenue, roi * 100])
        else:
            plt.bar(["Presupuesto", "Ingresos"], [budget, revenue])
        plt.title("Presupuesto vs Ingresos y ROI (%)")
        temp_path = f"{TEMP_DIR}/plot_{idx}.png"
        plt.savefig(temp_path)
        plt.close()
        story.append(Image(temp_path, width=250, height=180))

        # --- Sinopsis
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"📖 Sinopsis: {row.get('overview', 'No disponible')}", estilo_texto))

        story.append(PageBreak())

    doc.build(story)

    # 🔹 Limpiar carpeta temporal
    try:
        shutil.rmtree(TEMP_DIR)
    except FileNotFoundError:
        pass
    os.makedirs(TEMP_DIR, exist_ok=True)

    return filename
