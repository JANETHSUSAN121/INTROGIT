import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generar_informe_pdf(df_filtrado, filtros=None):
    # --- Crear documento PDF ---
    doc = SimpleDocTemplate("informe.pdf")
    styles = getSampleStyleSheet()
    story = []

    # --- Título ---
    story.append(Paragraph("Informe de Películas", styles["Title"]))
    story.append(Spacer(1, 12))

    # --- Filtros aplicados ---
    if filtros:
        story.append(Paragraph("Filtros aplicados:", styles["Heading2"]))
        for k, v in filtros.items():
            story.append(Paragraph(f"{k}: {v}", styles["Normal"]))
        story.append(Spacer(1, 12))

    # --- Tabla de resultados ---
    if not df_filtrado.empty:
        data = [["Título", "Director", "Año", "Género", "Score"]]
        for _, row in df_filtrado.iterrows():
            data.append([
                row.get("titulo", ""),
                row.get("Director", ""),
                row.get("Año", ""),
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
    return "informe.pdf"
    
