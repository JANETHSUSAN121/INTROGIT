import streamlit as st
import pandas as pd
import os

# -------------------------
# Configuración de la app
# -------------------------
st.set_page_config(page_title="Diccionario de Profesiones", layout="wide")
st.title("Diccionario de Profesiones en Jeroglíficos 🏺")
st.markdown("Selecciona una profesión para ver su jeroglífico, transliteración y descripción.")

# -------------------------
# Ruta del Excel
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "profesiones_jeroglificos.xlsx")

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel(EXCEL_PATH)
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        return pd.DataFrame()

df = cargar_datos()

# -------------------------
# Inicializar selección
# -------------------------
if "seleccion" not in st.session_state:
    st.session_state["seleccion"] = None

# -------------------------
# Layout: galería y panel de detalles
# -------------------------
galeria_col, detalles_col = st.columns([3, 2])
num_cols = 2
tarjetas = galeria_col.columns(num_cols)

# Galería de profesiones
for idx, fila in df.iterrows():
    col = tarjetas[idx % num_cols]
    with col:
        if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
            st.image(fila["Imagen"], width=200)  # miniatura
        if st.button(fila["profesion"], key=idx):
            st.session_state["seleccion"] = idx

# Panel de detalles
if st.session_state["seleccion"] is not None and not df.empty:
    fila = df.loc[st.session_state["seleccion"]]
    
    detalles_col.subheader(f"{fila['profesion']}")
    
    # Jeroglífico grande y centrado
    detalles_col.markdown(
        f"<p style='font-size:80px; text-align:center'>{fila['jeroglifico']}</p>",
        unsafe_allow_html=True
    )
    
    detalles_col.markdown(f"**Transliteración:** {fila['transliteracion']}")
    detalles_col.markdown(f"**Descripción:** {fila['descripcion']}")
    
    # Imagen grande del jeroglífico (si existe)
    if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
        detalles_col.image(fila["Imagen"], width=400)
