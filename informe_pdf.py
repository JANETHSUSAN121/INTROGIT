import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
import requests
import os

def generar_informe_pdf(df_filtrado, filtros=None):
    # --- Limpiar espacios y BOM, sin cambiar mayúsculas ---
    df_filtrado = df_filtrado.copy()
    df_filtrado.columns = df_filtrado.columns.str.strip().str.replace('\ufeff','', regex=True)

    # --- Asegurar columna 'Año' ---
    if "Año" not in df_filtrado.columns:
        df_filtrado["Año"] = pd.NA
    df_filtrado["Año"] = pd.to_numeric(df_filtrado["Año"], errors="coerce")

    # --- Eliminar duplicados ---
    df_filtrado = df_filtrado.drop_duplicates(subset=["titulo","director","Año"], keep="first")

    # --- Crear documento PDF ---
    filename = "Informe_Peliculas.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []

    # --- Estilos ---
    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_subtitulo = styles["Heading2"]
    estilo_texto = styles["Normal"]
    estilo_numeros = ParagraphStyle("Numeros", parent=styles["Normal"], fontSize=12, leading=16, spaceAfter=8, alignment=TA_LEFT)

    # --- Título del informe ---
    story.append(Paragraph("📊 Informe de Películas - Top Filtradas", estilo_titulo))
    story.append(Spacer(1, 20))

    # --- Filtros aplicados ---
    if filtros:
        story.append(Paragraph("Filtros aplicados:", estilo_subtitulo))
        for clave, val in filtros.items():
            story.append(Paragraph(f"<b>{clave}:</b> {val if val else 'Todos'}", estilo_texto))
            story.append(Spacer(1,5))
        story.append(Spacer(1,15))

    # --- Detalle de cada película ---
    for idx, row in df_filtrado.iterrows():
        story.append(Paragraph(f"🎬 {row.get('titulo','Sin título')}", estilo_subtitulo))
        story.append(Paragraph(f"Director: {row.get('director','N/A')} | Año: {row.get('Año','N/A')}", estilo_texto))
        story.append(Paragraph(f"Género: {row.get('genero','N/A')} | Estrellas: {row.get('estrellas','N/A')}", estilo_texto))
        story.append(Spacer(1,8))

        # --- Presupuesto, ingresos y ROI ---
        budget = row.get("budget",0) or 0
        revenue = row.get("revenue",0) or 0
        roi = (revenue-budget)/budget if budget>0 else None
        texto_numeros = f"<b>Presupuesto:</b> ${budget:,.0f}<br/><b>Ingresos:</b> ${revenue:,.0f}<br/><b>ROI:</b> {roi*100:.2f}%" if roi else "❌ ROI no disponible"
        story.append(Paragraph(texto_numeros, estilo_numeros))
        story.append(Spacer(1,5))

        # --- Poster ---
        poster_url = row.get("Poster_URL")  # columna exacta
        img = None

        if pd.notna(poster_url):
            try:
                response = requests.get(poster_url, timeout=5)
                if response.status_code == 200:
                    img = BytesIO(response.content)
            except:
                pass

        # Imagen por defecto si no hay poster válido
        if img is None:
            default_img_path = "poster_default.png"
            if os.path.exists(default_img_path):
                img = default_img_path

        # Solo agregar imagen si hay algo válido
        if img is not None:
            story.append(Image(img, width=200, height=300))
            story.append(Spacer(1,5))

        # --- Gráfico presupuesto vs ingresos ---
        plt.figure(figsize=(4,3))
        if roi:
            plt.bar(["Presupuesto","Ingresos","ROI (%)"], [budget,revenue,roi*100])
        else:
            plt.bar(["Presupuesto","Ingresos"], [budget,revenue])
        plt.title("Presupuesto vs Ingresos y ROI (%)")
        img_buf = BytesIO()
        plt.savefig(img_buf, format="png")
        plt.close()
        img_buf.seek(0)
        story.append(Image(img_buf, width=250, height=180))
        story.append(Spacer(1,10))

        # --- Sinopsis ---
        story.append(Paragraph(f"📖 Sinopsis: {row.get('overview','No disponible')}", estilo_texto))
        story.append(PageBreak())

    # --- Tabla resumen ---
    if not df_filtrado.empty:
        data = [["Título","Director","Año","Género","Score"]]
        for _, row in df_filtrado.iterrows():
            data.append([
                row.get("titulo",""),
                row.get("director",""),
                row.get("Año",""),
                row.get("genero",""),
                row.get("score","")
            ])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
            ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey)
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No se encontraron películas con los filtros aplicados.", styles["Normal"]))

    # --- Construir PDF ---
    doc.build(story)
    return filename
