from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import requests
from io import BytesIO
import pandas as pd

def generar_informe_pdf(df, filtros, nombre_archivo="informe_peliculas.pdf"):
    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # --- Título ---
    story.append(Paragraph("🎬 Informe de Películas", styles["Title"]))
    story.append(Spacer(1, 12))

    # --- Filtros aplicados ---
    story.append(Paragraph("<b>Filtros aplicados:</b>", styles["Heading2"]))
    for clave, valor in filtros.items():
        story.append(Paragraph(f"{clave}: {valor}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # --- Películas ---
    story.append(Paragraph("<b>Películas encontradas:</b>", styles["Heading2"]))

    for _, row in df.iterrows():
        elementos_pelicula = []

        # Imagen del póster (si existe)
        if "poster_url" in row and pd.notna(row["poster_url"]):
            try:
                response = requests.get(row["poster_url"], timeout=5)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = Image(img_data, width=100, height=150)  # 📌 tamaño del póster
                    elementos_pelicula.append(img)
            except Exception:
                pass

        # Información de la película
        info = []

        campos = {
            "titulo": "Título",
            "año": "Año",
            "director": "Director",
            "genero": "Género",
            "estrellas": "Estrellas",
            "roi": "ROI",
            "score": "Score",
            "productora": "Productora",
            "sinopsis": "Sinopsis"
        }

        for campo, etiqueta in campos.items():
            if campo in row and pd.notna(row[campo]):
                info.append(f"<b>{etiqueta}:</b> {row[campo]}")

        texto = Paragraph("<br/>".join(info), styles["Normal"])

        # Colocar imagen + texto en una fila
        fila = [elementos_pelicula[0] if elementos_pelicula else "", texto]
        tabla = Table([fila], colWidths=[110, 350])
        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.grey),
            ("INNERPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 12))

    # --- Guardar PDF ---
    doc.build(story)
    return nombre_archivo
