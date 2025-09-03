from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt
import tempfile
import os

def generar_informe_pdf(df, filtros):
    archivo_pdf = "informe_peliculas.pdf"
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", fontSize=16, leading=20, spaceAfter=10, alignment=1))
    styles.add(ParagraphStyle(name="Subtitulo", fontSize=12, leading=14, spaceAfter=6, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name="Normal", fontSize=10, leading=12))

    # --- Título general ---
    elementos.append(Paragraph("🎬 Informe de Películas", styles["Titulo"]))
    elementos.append(Spacer(1, 12))

    # --- Filtros aplicados ---
    filtros_texto = "<br/>".join([f"<b>{k}:</b> {v}" for k, v in filtros.items()])
    elementos.append(Paragraph("📌 Filtros aplicados:<br/>" + filtros_texto, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    # --- Recorrer películas ---
    for _, row in df.iterrows():
        titulo = row.get("titulo", "Desconocido")
        año = row.get("año", "N/A")
        director = row.get("director", "N/A")
        genero = row.get("genero", "N/A")
        estrellas = row.get("estrellas", "N/A")
        score = row.get("score", "N/A")
        productora = row.get("productora", "N/A")
        sinopsis = row.get("sinopsis", "Sin descripción disponible.")
        budget = row.get("budget", 0)
        revenue = row.get("revenue", 0)
        roi = row.get("roi", 0)
        poster_url = row.get("poster_url", None)

        # --- Título de la película ---
        elementos.append(Paragraph(f"🎞️ <b>{titulo}</b> ({año})", styles["Subtitulo"]))

        # --- Datos principales ---
        data = [
            ["Director", director],
            ["Género", genero],
            ["Estrellas", estrellas],
            ["Productora", productora],
            ["Score", score],
            ["Presupuesto", f"${budget:,.0f}"],
            ["Ingresos", f"${revenue:,.0f}"],
            ["ROI", f"{roi:.2f}%"]
        ]
        tabla = Table(data, colWidths=[100, 400])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("BOX", (0,0), (-1,-1), 0.5, colors.black),
            ("INNERGRID", (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 8))

        # --- Gráfico Budget vs Revenue ---
        if budget > 0 or revenue > 0:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.bar(["Budget", "Revenue"], [budget, revenue], color=["#FF6F61", "#6B8E23"])
            ax.set_ylabel("USD")
            ax.set_title("Comparación Budget vs Revenue")
            plt.tight_layout()

            temp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            plt.savefig(temp_chart.name, format="png")
            plt.close(fig)
            elementos.append(Image(temp_chart.name, width=300, height=150))
            elementos.append(Spacer(1, 8))

        # --- Sinopsis ---
        elementos.append(Paragraph("<b>Sinopsis:</b><br/>" + sinopsis, styles["Normal"]))
        elementos.append(Spacer(1, 15))

        # --- Póster si existe ---
        if poster_url and isinstance(poster_url, str) and poster_url.startswith("http"):
            try:
                from urllib.request import urlopen
                import io
                img_data = io.BytesIO(urlopen(poster_url).read())
                elementos.append(Image(img_data, width=150, height=200))
                elementos.append(Spacer(1, 15))
            except:
                elementos.append(Paragraph("⚠️ No se pudo cargar el póster.", styles["Normal"]))

        elementos.append(Spacer(1, 20))

    doc.build(elementos)
    return archivo_pdf
  

