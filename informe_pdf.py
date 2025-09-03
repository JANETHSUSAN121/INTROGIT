from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
import matplotlib.pyplot as plt
import tempfile
import requests
from io import BytesIO

def generar_informe_pdf(df, filtros):
    # Crear archivo temporal
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    elementos = []

    # Estilos
    styles = getSampleStyleSheet()
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 12

    # Cabecera con filtros
    elementos.append(Paragraph("🎬 Informe de Películas", styles["Title"]))
    elementos.append(Spacer(1, 12))
    filtros_texto = "<br/>".join([f"<b>{k}:</b> {v}" for k,v in filtros.items()])
    elementos.append(Paragraph(filtros_texto, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    for idx, row in df.iterrows():
        bloque = []

        # Título
        bloque.append(Paragraph(f"<b>{row['titulo']}</b> ({row['año']})", styles["Heading2"]))
        bloque.append(Spacer(1, 6))

        # Tabla de detalles
        tabla_data = [
            ["Director", row.get("director", "")],
            ["Género", row.get("genero", "")],
            ["Estrellas", row.get("estrellas", "")],
            ["ROI (%)", f"{row.get('roi', 0):.2f}"]
        ]
        tabla = Table(tabla_data, colWidths=[80, 400])
        tabla.setStyle(TableStyle([
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        bloque.append(tabla)
        bloque.append(Spacer(1, 6))

        # Poster si existe
        if "poster_url" in row and row["poster_url"]:
            try:
                response = requests.get(row["poster_url"])
                if response.status_code == 200:
                    img_temp = BytesIO(response.content)
                    bloque.append(Image(img_temp, width=120, height=180))
                    bloque.append(Spacer(1,6))
            except:
                pass

        # Gráfico Budget vs Revenue
        if "budget" in row and "revenue" in row and row["budget"] > 0:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.bar(["Budget", "Revenue"], [row["budget"], row["revenue"]], color=["orange","green"])
            ax.set_ylabel("USD")
            ax.set_title("Budget vs Revenue")
            plt.tight_layout()

            tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_img.name)
            plt.close(fig)
            bloque.append(Image(tmp_img.name, width=300, height=150))
            bloque.append(Spacer(1,6))

            # Valores exactos debajo del gráfico
            bloque.append(Paragraph(f"<b>Budget:</b> ${row['budget']:,} &nbsp;&nbsp; <b>Revenue:</b> ${row['revenue']:,}", styles["Normal"]))
            bloque.append(Spacer(1,6))

        # Sinopsis en recuadro
        if "overview" in row and row["overview"]:
            tabla_sinopsis = Table([[Paragraph(row["overview"], styles["Normal"])]], colWidths=[480])
            tabla_sinopsis.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('BACKGROUND',(0,0),(-1,-1),colors.whitesmoke),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),6),
                ('RIGHTPADDING',(0,0),(-1,-1),6),
                ('TOPPADDING',(0,0),(-1,-1),4),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ]))
            bloque.append(tabla_sinopsis)
            bloque.append(Spacer(1,12))

        elementos.append(KeepTogether(bloque))
        elementos.append(Spacer(1,12))

    # Generar PDF
    doc.build(elementos)
    return tmp.name
  
   
