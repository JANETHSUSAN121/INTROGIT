import streamlit as st
import pandas as pd

# -------------------------
# Configuración de la app
# -------------------------
st.set_page_config(page_title="Diccionario de Profesiones", layout="wide")
st.title("Diccionario de Profesiones en Jeroglíficos 🏺")
st.markdown("Selecciona una profesión para ver su jeroglífico, transliteración y descripción.")

# -------------------------
# Cargar Excel local
# -------------------------
@st.cache_data
def cargar_datos():
    try:
        # Asegúrate de que el Excel esté en la misma carpeta que este .py
        df = pd.read_excel("profesiones_jeroglificos.xlsx")
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
# Layout: galería y detalles
# -------------------------
galeria_col, detalles_col = st.columns([3, 2])

# Galería de tarjetas (2 tarjetas por fila)
num_cols = 2
tarjetas = galeria_col.columns(num_cols)

for idx, fila in df.iterrows():
    col = tarjetas[idx % num_cols]
    with col:
        if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
            st.image(fila["Imagen"], width=150)
        if st.button(fila["profesion"], key=idx):
            st.session_state["seleccion"] = idx

# -------------------------
# Mostrar detalles de la profesión seleccionada
# -------------------------
if st.session_state["seleccion"] is not None and not df.empty:
    fila = df.loc[st.session_state["seleccion"]]
    detalles_col.subheader(f"{fila['profesion']}")
    detalles_col.markdown(f"**Jeroglífico:** {fila['jeroglifico']}")
    detalles_col.markdown(f"**Transliteración:** {fila['transliteracion']}")
    detalles_col.markdown(f"**Descripción:** {fila['descripcion']}")
    if "Imagen" in df.columns and pd.notna(fila["Imagen"]):
        detalles_col.image(fila["Imagen"], use_column_width=True)
