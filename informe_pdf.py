from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
import matplotlib.pyplot as plt
import tempfile

def generar_informe_pdf(df, filtros):
    # Crear archivo temporal
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    elementos = []

    # Estilos
    styles = getSampleStyleSheet()
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 12

    # --- Cabecera con filtros ---
    elementos.append(Paragraph("🎬 Informe de Películas", styles["Title"]))
    elementos.append(Spacer(1, 12))
    filtros_texto = "<br/>".join([f"<b>{k}:</b> {v}" for k,v in filtros.items()])
    elementos.append(Paragraph(filtros_texto, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    for idx, row in df.iterrows():
        # Título
        elementos.append(Paragraph(f"<b>{row['titulo']}</b> ({row['año']})", styles["Heading2"]))
        elementos.append(Spacer(1, 6))

        # Tabla de detalles
        tabla_data = [
            ["Director", row.get("director", "")],
            ["Género", row.get("genero", "")],
            ["Estrellas", row.get("estrellas", "")],
            ["ROI (%)", f"{row.get('roi', 0):.2f}"]
        ]
        tabla = Table(tabla_data, colWidths=[80, 400])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 6))

        # Gráfico Budget vs Revenue
        if "budget" in row and "revenue" in row and row["budget"] > 0 and row["revenue"] >= 0:
            fig, ax = plt.subplots(figsize=(4,2))
            ax.bar(["Budget", "Revenue"], [row["budget"], row["revenue"]], color=["orange","green"])
            ax.set_ylabel("USD")
            ax.set_title("Budget vs Revenue")
            plt.tight_layout()

            # Guardar en archivo temporal
            tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_img.name)
            plt.close(fig)
            elementos.append(Image(tmp_img.name, width=300, height=150))
            elementos.append(Spacer(1, 6))

        # Sinopsis
        if "overview" in row:
            elementos.append(Paragraph(f"<b>Sinopsis:</b> {row['overview']}", styles["Normal"]))
            elementos.append(Spacer(1,12))

        elementos.append(Spacer(1,12))
    
    # Generar PDF
    doc.build(elementos)
    return tmp.name
  
  
   
